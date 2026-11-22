/* =========================================================
   wind.js — animation de vent (style solarpunk)
   - des traits de vent qui filent dans l'air
   - plusieurs sortes de feuilles emportées par des rafales :
     feuille ovale, feuille d'érable, feuille de ginkgo, pétale de cerisier
   Le dessin se fait dans un <canvas> placé derrière le contenu.
   ========================================================= */

(function () {
    "use strict";

    /* ---------- Réglages (modifie ici) ---------- */
    const CONFIG = {
        vitesseGlobale: 0.6,   // 1 = normal, 0.5 = deux fois plus lent
        nbFeuilles: 18,        // nombre de feuilles à l'écran
        nbTraits: 6,           // nombre de traits de vent en même temps
        vitesseVent: 1.3,      // vitesse de base du vent
        forceRafale: 1.8,      // force supplémentaire pendant une rafale
        couleurTrait: "255, 255, 255",   // blanc (format R, G, B)

        // sortes de feuilles : "poids" = fréquence d'apparition
        sortes: [
            { forme: "ovale",  poids: 3, couleurs: ["#6BB55A", "#8CC152", "#A3D16B"] },
            { forme: "erable", poids: 2, couleurs: ["#E8913A", "#F2C14E", "#D9622B"] },
            { forme: "ginkgo", poids: 2, couleurs: ["#F2C14E", "#C9D65A", "#E6B03A"] },
            { forme: "petale", poids: 3, couleurs: ["#F7A8C0", "#F9C6D5", "#FBD9E3"] },
        ],
    };

    // Respecte le réglage "réduire les animations" du système
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    /* ---------- Création du canvas ---------- */
    const canvas = document.createElement("canvas");
    canvas.id = "wind-canvas";
    Object.assign(canvas.style, {
        position: "fixed",
        inset: "0",
        width: "100%",
        height: "100%",
        zIndex: "-1",            // derrière le contenu de la page
        pointerEvents: "none",   // ne bloque pas les clics
    });
    document.body.appendChild(canvas);
    const ctx = canvas.getContext("2d");

    let largeur = 0, hauteur = 0;

    function redimensionner() {
        const ratio = window.devicePixelRatio || 1;
        largeur = window.innerWidth;
        hauteur = window.innerHeight;
        canvas.width = largeur * ratio;
        canvas.height = hauteur * ratio;
        ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    }
    window.addEventListener("resize", redimensionner);
    redimensionner();

    const hasard = (min, max) => min + Math.random() * (max - min);
    const auHasardDans = (liste) => liste[Math.floor(Math.random() * liste.length)];

    // choisit une sorte de feuille en tenant compte des "poids"
    function choisirSorte() {
        const total = CONFIG.sortes.reduce((somme, s) => somme + s.poids, 0);
        let tirage = Math.random() * total;
        for (const sorte of CONFIG.sortes) {
            tirage -= sorte.poids;
            if (tirage <= 0) return sorte;
        }
        return CONFIG.sortes[0];
    }

    /* ---------- Le vent : force qui varie avec des rafales ---------- */
    let temps = 0;
    let rafale = 0;            // 0 = calme, 1 = rafale maximale
    let rafaleCible = 0;
    let prochaineRafale = hasard(3, 6);

    function forceDuVent() {
        // petite ondulation permanente + rafale
        const ondulation = Math.sin(temps * 0.5) * 0.25 + Math.sin(temps * 1.3) * 0.12;
        return CONFIG.vitesseVent + ondulation + rafale * CONFIG.forceRafale;
    }

    function mettreAJourRafale(dt) {
        prochaineRafale -= dt;
        if (prochaineRafale <= 0) {
            rafaleCible = rafaleCible > 0 ? 0 : hasard(0.6, 1);   // alterne rafale / calme
            prochaineRafale = rafaleCible > 0 ? hasard(2, 4) : hasard(4, 8);
        }
        rafale += (rafaleCible - rafale) * Math.min(1, dt * 1.2);  // transition douce
    }

    /* ---------- Dessin des différentes formes ---------- */
    // Chaque fonction dessine une feuille centrée sur (0, 0), de taille t.
    const FORMES = {

        // feuille simple en amande, avec une nervure
        ovale(t) {
            ctx.beginPath();
            ctx.moveTo(-t, 0);
            ctx.quadraticCurveTo(0, -t * 0.8, t, 0);
            ctx.quadraticCurveTo(0, t * 0.8, -t, 0);
            ctx.fill();

            ctx.beginPath();
            ctx.moveTo(-t * 0.8, 0);
            ctx.lineTo(t * 0.8, 0);
            ctx.stroke();
        },

        // feuille d'érable : étoile à 5 pointes + petite tige
        erable(t) {
            ctx.beginPath();
            for (let i = 0; i < 10; i++) {
                const angle = -Math.PI / 2 + i * Math.PI / 5;
                const rayon = i % 2 === 0 ? t : t * 0.45;
                const x = Math.cos(angle) * rayon;
                const y = Math.sin(angle) * rayon;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.closePath();
            ctx.fill();

            ctx.beginPath();                    // tige + nervures
            ctx.moveTo(0, t * 1.1);
            ctx.lineTo(0, -t * 0.7);
            ctx.moveTo(0, 0);
            ctx.lineTo(-t * 0.6, -t * 0.2);
            ctx.moveTo(0, 0);
            ctx.lineTo(t * 0.6, -t * 0.2);
            ctx.stroke();
        },

        // feuille de ginkgo : éventail avec une encoche au milieu
        ginkgo(t) {
            const pointSur = (deg, r) => [Math.cos(deg * Math.PI / 180) * r, Math.sin(deg * Math.PI / 180) * r];
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(...pointSur(-150, t));
            ctx.arc(0, 0, t, -150 * Math.PI / 180, -96 * Math.PI / 180);
            ctx.lineTo(0, -t * 0.55);           // encoche
            ctx.lineTo(...pointSur(-84, t));
            ctx.arc(0, 0, t, -84 * Math.PI / 180, -30 * Math.PI / 180);
            ctx.closePath();
            ctx.fill();

            ctx.beginPath();                    // tige
            ctx.moveTo(0, 0);
            ctx.lineTo(0, t * 0.7);
            ctx.stroke();
        },

        // pétale de cerisier : goutte avec une petite encoche en haut
        petale(t) {
            ctx.beginPath();
            ctx.moveTo(0, t * 0.6);
            ctx.bezierCurveTo(-t * 0.9, 0, -t * 0.5, -t * 0.9, -t * 0.15, -t * 0.75);
            ctx.lineTo(0, -t * 0.55);
            ctx.lineTo(t * 0.15, -t * 0.75);
            ctx.bezierCurveTo(t * 0.5, -t * 0.9, t * 0.9, 0, 0, t * 0.6);
            ctx.fill();
        },
    };

    /* ---------- Feuilles ---------- */
    class Feuille {
        constructor(auDebut) {
            this.reinitialiser(auDebut);
        }

        reinitialiser(auDebut) {
            const sorte = choisirSorte();
            this.forme = sorte.forme;
            this.couleur = auHasardDans(sorte.couleurs);
            this.x = auDebut ? hasard(0, largeur) : hasard(-120, -20);
            this.y = hasard(0, hauteur * 0.85);
            this.taille = this.forme === "petale" ? hasard(7, 11) : hasard(9, 16);
            this.angle = hasard(0, Math.PI * 2);
            this.rotation = hasard(-1.2, 1.2);      // vitesse de rotation
            this.balancement = hasard(0, Math.PI * 2);
            this.poids = hasard(0.7, 1.3);          // les lourdes vont moins vite
            this.chute = hasard(6, 18);             // descente lente (px/s)
        }

        mettreAJour(dt, vent) {
            this.balancement += dt * 1.4;
            this.x += (vent * 50 / this.poids) * dt;
            this.y += (this.chute + Math.sin(this.balancement) * 25 - rafale * 20) * dt;
            this.angle += (this.rotation + vent * 0.3) * dt;

            // sortie de l'écran : on la renvoie à gauche
            if (this.x > largeur + 40 || this.y > hauteur + 40 || this.y < -60) {
                this.reinitialiser(false);
            }
        }

        dessiner() {
            ctx.save();
            ctx.translate(this.x, this.y);
            ctx.rotate(this.angle);
            ctx.scale(1, 0.55 + 0.45 * Math.abs(Math.sin(this.balancement)));  // effet 3D qui tourne

            ctx.fillStyle = this.couleur;
            ctx.strokeStyle = "rgba(255, 255, 255, 0.55)";
            ctx.lineWidth = 1;
            ctx.lineCap = "round";
            FORMES[this.forme](this.taille);
            ctx.restore();
        }
    }

    /* ---------- Traits de vent ---------- */
    class Trait {
        constructor(auDebut) {
            this.reinitialiser(auDebut);
        }

        reinitialiser(auDebut) {
            this.x = auDebut ? hasard(-largeur * 0.3, largeur) : hasard(-400, -150);
            this.y = hasard(hauteur * 0.05, hauteur * 0.9);
            this.longueur = hasard(120, 260);
            this.amplitude = hasard(6, 18);         // hauteur des vagues
            this.frequence = hasard(0.012, 0.025);
            this.vitesse = hasard(0.8, 1.2);
            this.epaisseur = hasard(1.5, 3);
            this.boucle = Math.random() < 0.35;     // certains finissent par une boucle
            this.historique = [];                   // positions passées = la traînée
        }

        mettreAJour(dt, vent) {
            this.x += vent * 110 * this.vitesse * dt;
            const yVague = this.y + Math.sin(this.x * this.frequence) * this.amplitude;
            this.historique.push({ x: this.x, y: yVague });

            // garde seulement la longueur de la traînée
            while (this.historique.length > 2) {
                const premier = this.historique[0];
                if (this.x - premier.x > this.longueur) this.historique.shift();
                else break;
            }

            if (this.x - this.longueur > largeur + 50) this.reinitialiser(false);
        }

        dessiner() {
            const pts = this.historique;
            if (pts.length < 2) return;

            ctx.lineCap = "round";
            ctx.lineWidth = this.epaisseur;

            // la traînée s'efface vers l'arrière
            for (let i = 1; i < pts.length; i++) {
                const opacite = (i / pts.length) * 0.75 * (0.5 + rafale * 0.5);
                ctx.strokeStyle = `rgba(${CONFIG.couleurTrait}, ${opacite})`;
                ctx.beginPath();
                ctx.moveTo(pts[i - 1].x, pts[i - 1].y);
                ctx.lineTo(pts[i].x, pts[i].y);
                ctx.stroke();
            }

            // petite boucle au bout du trait (style cartoon)
            if (this.boucle && pts.length > 10) {
                const fin = pts[pts.length - 1];
                ctx.strokeStyle = `rgba(${CONFIG.couleurTrait}, ${0.7 * (0.5 + rafale * 0.5)})`;
                ctx.beginPath();
                ctx.arc(fin.x - 6, fin.y - 8, 8, Math.PI * 0.5, Math.PI * 2.2);
                ctx.stroke();
            }
        }
    }

    /* ---------- Boucle d'animation ---------- */
    const feuilles = Array.from({ length: CONFIG.nbFeuilles }, () => new Feuille(true));
    const traits = Array.from({ length: CONFIG.nbTraits }, () => new Trait(true));

    let dernier = performance.now();

    function animer(maintenant) {
        // dt = temps écoulé en secondes (limité si l'onglet était en arrière-plan),
        // multiplié par vitesseGlobale pour ralentir ou accélérer toute l'animation
        const dt = Math.min((maintenant - dernier) / 1000, 0.05) * CONFIG.vitesseGlobale;
        dernier = maintenant;
        temps += dt;

        mettreAJourRafale(dt);
        const vent = forceDuVent();

        ctx.clearRect(0, 0, largeur, hauteur);

        traits.forEach(t => { t.mettreAJour(dt, vent); t.dessiner(); });
        feuilles.forEach(f => { f.mettreAJour(dt, vent); f.dessiner(); });

        requestAnimationFrame(animer);
    }

    requestAnimationFrame(animer);
})();
