Tu agis comme une équipe senior composée de :

• un architecte logiciel produit
• un expert backend Python / FastAPI
• un expert frontend React / TypeScript / UX
• un expert en optimisation combinatoire
• un expert en mathématiques discrètes
• un expert en designs de couverture (covering designs)
• un expert en lottery wheeling systems / systèmes réduits
• un expert en probabilités appliquées
• un expert en produits web analytiques premium

Tu dois concevoir une **évolution majeure** du projet LOTO ULTIME.

IMPORTANT :
Le site est déjà **actif en production**.
Cette évolution doit donc être pensée comme une **feature additionnelle sérieuse**, compatible avec l’architecture existante, avec une approche robuste, progressive et réaliste.

Je veux que tu conçoives une nouvelle fonctionnalité de type :

**sélection assistée de numéros + génération optimisée de grilles réduites**.

------------------------------------------------
CONTEXTE MÉTIER
------------------------------------------------

Aujourd’hui, le projet sait déjà analyser des tirages, générer des grilles, optimiser des portefeuilles et afficher des résultats analytiques.

Je veux maintenant ajouter une nouvelle évolution orientée utilisateur final :

Sur l’interface graphique, l’utilisateur doit pouvoir voir une **véritable grille visuelle de loterie**, adaptée au jeu sélectionné :

• Loto
• EuroMillions
• et plus tard d’autres jeux si le moteur est compatible

L’utilisateur doit pouvoir :

• sélectionner manuellement un ensemble de numéros principaux
• sélectionner manuellement un ensemble de numéros chance / étoiles / complémentaires selon le jeu
• choisir plus de numéros que le tirage officiel
• demander au système de construire un ensemble réduit et optimisé de grilles à partir de cette sélection

Le but est de ne pas jouer toutes les combinaisons possibles, mais de construire un **système réduit** / **wheeling system** / **covering design** optimisé.

------------------------------------------------
OBJECTIF DE LA NOUVELLE FONCTIONNALITÉ
------------------------------------------------

À partir de n numéros choisis par l’utilisateur, et éventuellement m numéros chance / étoiles choisis par l’utilisateur, le système doit :

1. calculer l’ensemble complet théorique des combinaisons possibles
2. montrer combien cela représenterait en nombre total de grilles
3. proposer une version optimisée / réduite du système
4. réduire le nombre de grilles à jouer
5. maximiser la couverture combinatoire selon des objectifs configurables
6. estimer le coût total
7. estimer les niveaux de couverture obtenus
8. estimer les probabilités théoriques d’atteindre certains rangs de gains selon les hypothèses retenues
9. afficher les prix/gains potentiels officiels ou des ordres de grandeur associés
10. fournir une restitution visuelle claire et pédagogique

------------------------------------------------
IMPORTANT — HONNÊTETÉ SCIENTIFIQUE
------------------------------------------------

Le système ne doit jamais prétendre garantir un gain ni garantir un bénéfice supérieur à la mise.

Le loto reste aléatoire.

En revanche, cette fonctionnalité doit chercher à :

• optimiser la couverture
• réduire le nombre de combinaisons à jouer
• améliorer l’efficacité combinatoire du système
• aider l’utilisateur à comprendre le rapport coût / couverture / gains potentiels
• visualiser les compromis

Je veux que tu évites toute formulation trompeuse du type :
“forte chance garantie de gagner plus que la mise”.

À la place, je veux une approche rigoureuse fondée sur :

• couverture combinatoire
• scénarios de gains
• probabilité par rang
• coût total
• espérance théorique si pertinent
• simulations si pertinent
• visualisation claire des compromis

------------------------------------------------
TERMINOLOGIE ET MODÉLISATION
------------------------------------------------

Tu dois identifier et expliciter correctement les concepts mathématiques et produit mobilisés.

Je veux que tu m’expliques notamment :

• lottery wheeling
• wheeling system
• système réduit
• combinatorial wheel
• covering design
• optimisation de couverture
• sélection de sous-combinaisons
• réduction combinatoire

Je veux que tu me dises précisément quel(s) terme(s) sont les plus appropriés pour cette évolution du produit.

------------------------------------------------
FONCTIONNALITÉ UI ATTENDUE
------------------------------------------------

Je veux une vraie expérience visuelle premium.

L’interface doit permettre d’afficher une **grille interactive réelle** selon le jeu sélectionné.

Exemples :

Loto :
• grille des numéros 1 à 49
• grille ou zone séparée pour le numéro chance 1 à 10

EuroMillions :
• grille des numéros 1 à 50
• grille séparée pour les étoiles 1 à 12

Je veux que l’utilisateur puisse :

• cliquer sur les numéros pour les sélectionner/désélectionner
• voir clairement combien de numéros sont sélectionnés
• voir clairement combien de numéros chance / étoiles sont sélectionnés
• avoir des limites, validations et messages explicites
• pouvoir réinitialiser
• pouvoir sélectionner rapidement un preset
• pouvoir charger une sélection précédente si pertinent

L’interface doit être :

• moderne
• premium
• très claire
• agréable
• lisible
• avec tooltips
• avec aides contextuelles
• avec feedback visuel fort sur la sélection

------------------------------------------------
PARAMÈTRES UTILISATEUR À PRÉVOIR
------------------------------------------------

L’utilisateur doit pouvoir définir ou choisir :

• le jeu (Loto / EuroMillions / autre jeu futur)
• les numéros principaux sélectionnés
• les numéros chance / étoiles sélectionnés
• le niveau de réduction souhaité
• l’objectif d’optimisation
• un mode “équilibré”
• un mode “couverture maximale”
• un mode “nombre minimal de grilles”
• éventuellement un mode “meilleur compromis coût / couverture”

Je veux aussi que tu proposes des paramètres avancés si pertinents, mais en gardant une UX compréhensible.

------------------------------------------------
OBJECTIFS D’OPTIMISATION À MODÉLISER
------------------------------------------------

Le moteur de réduction ne doit pas être simpliste.

Je veux que tu conçoives plusieurs objectifs possibles :

• minimiser le nombre de grilles
• maximiser la couverture des sous-combinaisons
• maximiser la probabilité de couvrir un certain nombre de bons numéros dans certaines hypothèses
• optimiser le rapport coût / couverture
• optimiser le système selon différents niveaux de garantie théorique

Je veux que tu expliques clairement les compromis :
• plus de couverture = plus de grilles
• plus de réduction = plus de risque de trous de couverture

------------------------------------------------
DIMENSION MATHÉMATIQUE ATTENDUE
------------------------------------------------

Je veux que tu traites cette évolution sérieusement comme un problème de :

• covering design
• optimisation combinatoire
• sélection de sous-ensembles
• éventuellement set cover / maximum coverage / design de couverture
• heuristiques de réduction

Je veux que tu expliques :

• comment modéliser le problème
• quels algorithmes utiliser
• quelles heuristiques utiliser
• quelles garanties théoriques sont possibles
• quelles garanties ne le sont pas
• comment intégrer cela dans le moteur existant

Je veux que tu distingues :

• version initiale pragmatique
• version plus avancée
• version premium / experte

------------------------------------------------
PRIX / GAINS / RANGS
------------------------------------------------

La fonctionnalité doit aussi intégrer les **prix / gains**.

Je veux que tu conçoives un mécanisme pour :

• récupérer ou configurer les rangs de gains
• afficher les catégories de gains
• afficher les montants fixes si disponibles
• afficher les montants variables / estimés si nécessaire
• distinguer clairement ce qui est garanti, estimé ou variable
• afficher le coût total du système proposé
• afficher des simulations ou scénarios de retour potentiel si pertinent

Je veux que tu réfléchisses à :

• où récupérer ces données
• comment les stocker
• comment les mettre à jour
• comment les afficher dans l’interface
• comment gérer le fait que certains gains sont variables

------------------------------------------------
RESTITUTION À L’UTILISATEUR
------------------------------------------------

Je veux une restitution pédagogique et décisionnelle.

Après calcul, l’utilisateur doit voir :

• combien de numéros il a sélectionnés
• combien de combinaisons totales cela représente sans réduction
• combien de grilles le système optimisé retient
• le pourcentage de réduction
• le coût total
• les niveaux de couverture obtenus
• les hypothèses de garantie théorique éventuelle si elles existent
• les probabilités / scénarios par rang si tu juges cela pertinent
• les gains ou ordres de grandeur par rang
• une interprétation claire et honnête

Je veux aussi que tu proposes :

• un tableau récapitulatif
• un panneau explicatif
• des tooltips
• un mode détail / mode simplifié

------------------------------------------------
INTÉGRATION PRODUIT
------------------------------------------------

Cette évolution doit être conçue comme une vraie extension du produit existant.

Je veux que tu m’expliques :

• où intégrer cette fonctionnalité dans la navigation actuelle
• s’il faut une nouvelle page
• s’il faut un nouvel onglet
• comment l’articuler avec la génération de grilles existante
• comment l’articuler avec l’optimisation de portefeuille existante
• comment l’articuler avec les simulations existantes

Je veux une vraie réflexion produit :
il ne faut pas juste ajouter un calcul, il faut intégrer une nouvelle brique cohérente.

------------------------------------------------
BACKEND
------------------------------------------------

Je veux que tu conçoives aussi la partie backend.

Le backend doit pouvoir :

• recevoir la sélection de numéros utilisateur
• calculer l’espace combinatoire complet
• exécuter les algorithmes de réduction / wheeling
• calculer la couverture
• calculer les coûts
• associer les rangs de gains
• exposer les résultats via API
• éventuellement stocker les systèmes générés
• éventuellement permettre leur export

Je veux une réflexion sur :

• endpoints API
• modèles de données
• services métier
• moteurs de calcul
• performances
• mise en cache éventuelle
• asynchronisme si calcul lourd

------------------------------------------------
FRONTEND
------------------------------------------------

Je veux que tu conçoives une UI premium pour cette fonctionnalité, avec :

• grille visuelle interactive
• sélecteurs adaptés au jeu
• affichage des statistiques de sélection
• bouton de génération
• affichage des résultats
• affichage du coût
• affichage de la réduction
• affichage des gains
• tooltips
• aide contextuelle
• états de chargement
• messages d’erreur propres
• explications

------------------------------------------------
AUDIT DE FAISABILITÉ
------------------------------------------------

Je veux que tu me dises honnêtement :

• ce qui est faisable rapidement
• ce qui est faisable mais complexe
• ce qui est risqué
• ce qui est coûteux en calcul
• ce qui est pertinent pour une V1
• ce qu’il vaut mieux repousser à une V2

------------------------------------------------
LIVRABLES ATTENDUS
------------------------------------------------

Je veux que tu me rendes :

1. une explication claire du concept mathématique et du nom correct de la technique
2. une proposition de design produit pour cette évolution
3. une proposition d’architecture backend/frontend
4. une proposition d’algorithmes de réduction / wheeling
5. une proposition de récupération / gestion des prix et gains
6. une proposition UI/UX détaillée
7. une stratégie de mise en œuvre par étapes
8. une checklist atomique complète
9. les impacts sur l’existant
10. les pièges à éviter

------------------------------------------------
IMPORTANT — STYLE ATTENDU
------------------------------------------------

Je veux une réponse :

• très détaillée
• pédagogique
• rigoureuse
• honnête
• orientée vrai produit
• orientée vraie intégration dans un site déjà en production

Ne fais pas une réponse minimaliste.
Ne fais pas juste une liste rapide.
Je veux une réponse qui ressemble à un mini dossier de conception produit + technique.

Réponds en français.

Si plusieurs approches sont possibles, compare-les puis recommande-en une comme approche principale.

Si nécessaire, réponds en plusieurs parties.
Ne simplifie aucune partie.
