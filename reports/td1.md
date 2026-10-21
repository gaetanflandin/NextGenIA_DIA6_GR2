# Rapport TD1 — SQL généré par cinq modèles

Date : 21 octobre 2026. Dépôt : https://github.com/gaetanflandin/NextGenIA_DIA6_GR2

## Travail réalisé et livrables

Nous avons préparé vingt références SQL, exécuté les vingt questions auprès de chacun des cinq modèles requis, puis consolidé les traces et les synthèses. Le lot contient 100 tentatives réelles : 60 Groq et 40 OpenRouter. Il ne contient ni rejeu ni simulation. Aucun nouvel appel aux modèles n'a été nécessaire pour construire les synthèses.

- [Références exécutées et montants](../reference-td1.csv) : vingt questions, une requête et une valeur par question.
- [Questions et requêtes SQL](../questions-td1.sql).
- [Traces consolidées](../traces-td1.csv) : une ligne par tentative, avec les mesures absentes laissées vides.
- [Comparaison longue](../model-question-comparison-en.csv) : 100 résultats finaux, explications et liens logiques vers les traces brutes par fichier et `cell_id`.
- [Synthèse des cinq modèles](../five-model-summary-en.csv) : résultats par famille, indices, tarifs, sources et limites.
- [Notebook de contrôle et de présentation](../comparaison.ipynb) : contrôle SQL/CSV, comparaison du modèle E et vues de synthèse préparées pour la plénière.
- [Squelette et prompts utilisés](../skeleton-multi-llm-en.py) : `SYSTEM_PROMPT`, `USER_PROMPT_TEMPLATE` et `build_prompt` ; [configuration des modèles](../modeles-autorises.json).

## Références et conventions

Les vingt requêtes ont été exécutées sur `data/boutique.sqlite`, en lecture seule. Chaque requête renvoie une ligne et une colonne entière `revenue_cents`. Un calcul Python distinct sur les trois CSV vérifie les montants sans utiliser les réponses des modèles évalués : vingt concordances sur vingt lors du contrôle.

Les périodes sont en UTC, début inclus et fin exclue. L'âge est révolu au mois et au jour ; la date de référence est celle de la question, sauf demande explicite de l'âge à la commande. Les produits sont filtrés ligne par ligne. Le montant est la somme quantité × prix unitaire HT, en centimes, avec zéro pour un ensemble vide.

La relecture indépendante entre membres et la comparaison au corrigé enseignant doivent être confirmées par le groupe : l'exécution locale ne prouve pas à elle seule l'égalité avec ce corrigé. La répartition nominative des vingt questions et les signatures de relecture ne sont pas documentées dans les fichiers examinés.

## Résultats du lot

| Opérateur | Modèle | Correctes | Montants incorrects | SQL invalides | Taux |
|---|---|---:|---:|---:|---:|
| A | GPT-OSS 120B, Groq | 19 | 1 | 0 | 95 % |
| B | GPT-OSS 20B, Groq | 18 | 2 | 0 | 90 % |
| C | Cohere North Mini Code, OpenRouter | 13 | 6 | 1 | 65 % |
| D | Qwen3.8-27B, Groq | 14 | 6 | 0 | 70 % |
| E | Dots3-Note Preview, OpenRouter | 12 | 6 | 2 | 60 % |
| Total | 100 cellules | 76 | 21 | 3 | 76 % |

Les 100 appels enregistrés ont un statut HTTP 200. Chaque cellule a une seule tentative : 100 appels initiaux, zéro reprise dans ce lot. Les requêtes invalides sont des échecs SQL après une réponse HTTP réussie, pas des échecs d'accès.

Les familles sont exclusives et suivent les types de `questions-td1.json` : six questions de période seule, cinq d'âge seul, quatre de produits (avec leur période lorsqu'elle est explicitement demandée), cinq de filtres combinés. Tous les modèles réussissent les six périodes seules et les quatre questions produits ; les erreurs du lot concernent l'âge ou ses combinaisons. Les dénominateurs sont conservés dans la synthèse.

## Causes observées et preuves

Les explications détaillées figurent dans les lignes de [model-question-comparison-en.csv](../model-question-comparison-en.csv), sans ajouter de troisième tableau d'erreurs obligatoire.

- A/C19 : le SQL teste `birth_date = date('2026-09-25', '-25 years')`. Il ne sélectionne que les anniversaires du jour au lieu de tous les clients de 25 ans ; résultat 0 contre référence 1990. Preuve : [state-A.jsonl](../state-A.jsonl), `groq:openai/gpt-oss-120b:C19`.
- B/C02 : les bornes de naissance sont en 2025–2026, au lieu de sélectionner des clients ayant 25 ans en 2026. Preuve : [state-B.jsonl](../state-B.jsonl), `groq:openai/gpt-oss-20b:C02`.
- C/C02 : un alias `AS age` est inséré dans `WHERE`, ce qui produit une erreur de syntaxe SQLite. Preuve : [state-C.jsonl](../state-C.jsonl), `openrouter:cohere/north-mini-code:free:C02`.
- D/C15 : le mois-jour de naissance doit être à la fois inférieur ou égal et strictement supérieur au 25 septembre ; le filtre est contradictoire. Preuve : [state-D.jsonl](../state-D.jsonl), `groq:qwen/qwen3.8-27b:C15`.
- E/C10 : hors 29 février, absent des données, le filtre exige que le mois-jour de commande soit à la fois supérieur ou égal et strictement inférieur au même anniversaire. Preuve : [state-E.jsonl](../state-E.jsonl), `openrouter:dots-studio/dots-3-note-preview:free:C10`.

Questions manquées par la majorité : C19 (4/5), C08, C09, C10 et C17 (3/5 chacune). C19 inclut un SQL invalide ; les autres erreurs de majorité sont des montants incorrects. Ces questions et leurs conventions d'âge seront reprises au TD2.

Deux modèles s'accordent sur une même valeur fausse pour C08 (0), C09 (0) et C10 (119410). Il s'agit d'accords partiels, pas d'un consensus majoritaire de trois modèles sur cinq. Le vote reste à étudier au TD2.

## Traçabilité, accès et limites du protocole

L'empreinte est le SHA-256 du message système, d'un saut de ligne et du message utilisateur, encodés en UTF-8. Le message utilisateur inclut le schéma, les conventions et la question. Les empreintes ont été vérifiées : pour chaque question, les cinq modèles partagent la même empreinte et la même référence. Cette égalité n'est pas une garantie de justesse des réponses.

Les cinq CSV sources et les cinq JSONL sont conservés : [A CSV](../traces-A.csv), [A JSONL](../state-A.jsonl), [B CSV](../traces-B.csv), [B JSONL](../state-B.jsonl), [C CSV](../traces-C.csv), [C JSONL](../state-C.jsonl), [D CSV](../traces-D.csv), [D JSONL](../state-D.jsonl), [E CSV](../traces_E.CSV), [E JSONL](../state-E.jsonl). Le CSV B est abrégé ; la consolidation utilise son JSONL complet, sans inventer les champs absents. Les autres différences de retours à la ligne SQL entre CSV et JSONL n'affectent pas les montants.

Le squelette prévoit la température 0, trois secondes entre requêtes, 45 secondes de timeout et au plus une reprise par cellule sur les reprises d'exécution. Les plafonds et paramètres de raisonnement sont ceux du JSON fourni. Les traces n'enregistrent pas le corps HTTP complet ; elles ne prouvent donc pas indépendamment tous les paramètres utilisés par chaque opérateur.

**Écart de coordination à déclarer :** les horodatages de fin et les latences suggèrent un chevauchement entre E/C01 et B/C19 vers 13:20 UTC (15:20 à Paris). Les horodatages étant à la seconde, il s'agit d'une estimation ; la règle collective d'une seule requête en cours ne peut pas être attestée sur tout le lot. Les traces originales ne sont pas modifiées pour masquer cet écart.

Le membre E a déclaré utiliser un compte personnel distinct. Avant son lot, le compteur OpenRouter indiquait 6 appels gratuits déjà utilisés et 44 disponibles, assez pour 20 cellules et une marge cible de 5. L'origine des 6 appels antérieurs reste à préciser ; ils ne sont pas assimilés sans preuve à des contrôles d'accès. Les compteurs avant/après et les contrôles d'accès des autres membres restent à documenter.

Les 60 traces Groq n'ont pas de coût natif fourni : ces cellules restent vides. Une mesure absente n'est pas zéro. Les prix de routes payantes de la synthèse sont des informations de catalogue distinctes du coût réellement mesuré.

L'audit a détecté des conversions Git LF/CRLF dans les trois CSV de données et `schema.sql`. Les fins de ligne ont été restaurées au format attendu ; `verify-data.py` a alors confirmé toutes les empreintes, l'intégrité SQLite et les clés étrangères. Les données logiques et la base SQLite n'ont pas été modifiées.

## Portefeuille et hypothèse de routage

Le [portefeuille fourni](../portefeuille-modeles-en.md) est conservé. Les indices de GPT-OSS et Qwen viennent de sa photographie du 28 septembre 2026 ; sa source ne fournit pas l'URL précise du classement historique. Aucun indice comparable documenté n'est inventé pour Cohere et Dots.

Les tarifs payants documentés pour les mêmes identifiants GPT-OSS et Qwen ont été consultés le 21 octobre 2026 dans le [catalogue Groq](https://console.groq.com/docs/models). Les pages consultées pour [Cohere](https://openrouter.ai/cohere/north-mini-code:free) et [Dots](https://openrouter.ai/dots-studio/dots-3-note-preview:free) ne documentent que les routes gratuites : les tarifs payants sont N/A, avec justification. Les dates et sources figurent dans la synthèse.

Hypothèse limitée à ce lot : tester une route gratuite pour les périodes et produits, avec validation SQL systématique ; renforcer la vérification des âges et des combinaisons. A réussit les cinq questions d'âge seul et B les cinq combinaisons, mais vingt questions par modèle ne permettent ni garantie de généralisation ni classement général. Une requête déterministe fiable reste préférable lorsqu'elle est disponible.

## Contributions et assistance

Les identités des opérateurs A–D et la répartition nominative des autres travaux restent à confirmer par le groupe ; les traces attestent les lots, pas leur auteur humain.

| Rôle | Contribution attestée par les fichiers | Personne |
|---|---|---|
| A | Lot GPT-OSS 120B, 20 cellules | À renseigner |
| B | Lot GPT-OSS 20B, 20 cellules | À renseigner |
| C | Lot Cohere, 20 cellules | À renseigner |
| D | Lot Qwen, 20 cellules | À renseigner |
| E | Lot Dots, 20 cellules ; préparation des références et consolidation avec assistance | Gaëtan, identité à confirmer par le groupe |
| Autres membres | Relectures indépendantes, coordination et présentation | Noms et tâches à renseigner |

Codex a assisté le code des références, les contrôles CSV, le notebook, la consolidation, les explications et ce rapport. Les montants de référence proviennent d'exécutions SQL contrôlées sur CSV, pas de l'acceptation d'un montant proposé par un modèle. Le groupe doit relire, comprendre et valider les livrables. L'approbation scolaire de cette assistance reste à confirmer.

## Travail restant et préparation du TD2

- Confirmer la relecture entre membres, la validation des références par l'enseignant et l'autorisation d'assistance.
- Présenter la matrice et la synthèse ; documenter les écarts réellement observés entre sous-groupes. Aucune trace d'un autre sous-groupe n'est disponible ici.
- Faire renseigner R1, R2 et R3 par l'enseignant sur la fiche officielle ; aucun score n'est attribué dans ce rapport.
- Aucun échec d'accès n'ayant été observé, demander pour R3 un exemple historique ou simulé identifié fourni par l'enseignant et le distinguer du lot réel. Aucun exemple de ce type n'a été ajouté aux mesures.
- Désigner le responsable TD2 : **à renseigner avant de partir**. Récupérer et lire `atelier-vote.py` et la règle de routage attendue : cet atelier est absent du dépôt examiné. Examiner aussi `Orchestrateur.vote_k_sur_n` dans le squelette.
- Étudier les votes et désaccords sur les traces existantes, sans nouvel appel obligatoire ; reprendre les conventions d'âge des questions difficiles.
- Compléter les contributions et les compteurs d'accès, puis commiter et pousser le rapport avec les livrables. Le commit final ne sera connu qu'après cette étape.
- Vérifier que le dépôt est accessible sans connexion et mettre à jour Moodle avec l'URL complète, le hash complet du commit de rendu et un lien vers `reports/td1.md` à ce commit. Ces actions de remise ne sont pas attestées par la création de ce rapport.
