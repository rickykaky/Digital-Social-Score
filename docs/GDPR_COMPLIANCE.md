# RGPD / GDPR Compliance Documentation

## Vue d'ensemble de la conformité RGPD

L'API Digital Social Score est conçue pour être conforme au Règlement Général sur la Protection des Données (RGPD / GDPR). Ce document détaille les mesures de protection mises en place.

## Principes fondamentaux respectés

### 1. Minimisation des données (Article 5.1.c)

**Mise en œuvre :**
- L'API traite uniquement le texte soumis
- Aucune donnée d'identification directe n'est collectée
- Pas de tracking utilisateur
- Pas de cookies de suivi

**Justification :** Seules les données strictement nécessaires à l'analyse de toxicité sont traitées.

### 2. Limitation de la conservation (Article 5.1.e)

**Mise en œuvre :**
- Aucune donnée n'est conservée après le traitement de la requête
- Pas de base de données de stockage
- Logs ne contiennent pas de données personnelles
- TTL (Time To Live) : 0 seconde après la réponse

**Justification :** Les données sont traitées en temps réel et immédiatement supprimées.

### 3. Intégrité et confidentialité (Article 5.1.f)

**Mise en œuvre :**
- Anonymisation automatique des PII avant traitement ML
- HTTPS/TLS en production
- Pas de logs de données personnelles
- Secrets chiffrés (clés API, credentials)

**Justification :** Protection technique contre l'accès non autorisé.

## Traitement des données personnelles

### Types de données traitées

| Type de donnée | Traitement | Conservation |
|----------------|------------|--------------|
| Texte soumis | Analyse temporaire | Non conservé |
| PII détectées | Anonymisation immédiate | Non conservé |
| Métadonnées requête | Métriques agrégées uniquement | Non conservé |

### Catégories de PII détectées et anonymisées

1. **Identifiants directs**
   - Noms de personnes (PERSON)
   - Adresses email (EMAIL)
   - Numéros de téléphone (PHONE)
   - Adresses IP (IP_ADDRESS)

2. **Identifiants indirects**
   - Organisations (ORG)
   - Lieux spécifiques (GPE, LOC)
   - Dates spécifiques (DATE)

### Méthodes d'anonymisation

#### 1. Masking (par défaut)
```
Original: "Contactez Jean Dupont au 01-23-45-67-89"
Anonymisé: "Contactez [PERSON] au [PHONE]"
```

**Propriétés :**
- Irréversible
- Préserve la structure du texte
- RGPD compliant

#### 2. Pseudonymisation
```
Original: "Contactez Jean Dupont au 01-23-45-67-89"
Anonymisé: "Contactez [PERSON_a3f5b8c2] au [PHONE_7d9e4f1a]"
```

**Propriétés :**
- Hash consistant (même entrée = même sortie)
- Permet le suivi anonyme si nécessaire
- RGPD compliant avec mesures techniques

#### 3. Suppression
```
Original: "Contactez Jean Dupont au 01-23-45-67-89"
Anonymisé: "Contactez  au "
```

**Propriétés :**
- Suppression complète
- Perte potentielle de contexte
- Maximum de protection

## Base légale du traitement

### Intérêt légitime (Article 6.1.f)

**Finalités :**
- Modération de contenu
- Détection de contenus toxiques
- Protection des utilisateurs

**Mise en balance :**
- **Intérêt poursuivi :** Sécurité et bien-être des utilisateurs
- **Impact sur les droits :** Minimal (anonymisation automatique)
- **Conclusion :** Intérêt légitime proportionné et justifié

## Droits des personnes concernées

### Droit d'accès (Article 15)
**Réponse :** Aucune donnée personnelle n'est conservée. L'API ne peut donc pas fournir d'accès à des données inexistantes.

### Droit de rectification (Article 16)
**Réponse :** Non applicable - pas de conservation de données.

### Droit à l'effacement (Article 17)
**Réponse :** Automatiquement respecté - les données sont effacées immédiatement après traitement.

### Droit à la limitation du traitement (Article 18)
**Réponse :** L'utilisateur peut désactiver l'anonymisation (non recommandé) via le paramètre `anonymize: false`.

### Droit à la portabilité (Article 20)
**Réponse :** Non applicable - pas de conservation de données.

### Droit d'opposition (Article 21)
**Réponse :** L'utilisateur peut choisir de ne pas utiliser le service.

## Registre des activités de traitement

### Identité du responsable de traitement
- **Nom :** [À compléter par l'organisation utilisatrice]
- **Adresse :** [À compléter]
- **Contact DPO :** [À compléter]

### Description du traitement

| Élément | Description |
|---------|-------------|
| **Nom du traitement** | Analyse de toxicité de texte |
| **Finalité** | Détection de contenu toxique, modération |
| **Base légale** | Intérêt légitime (Article 6.1.f) |
| **Catégories de données** | Textes utilisateur, contenu potentiellement toxique |
| **Catégories de personnes** | Auteurs de contenus textuels |
| **Destinataires** | Système d'IA de l'API (traitement automatisé) |
| **Transferts hors UE** | Non (sauf si modèles hébergés hors UE) |
| **Durée de conservation** | 0 seconde (traitement temps réel uniquement) |
| **Mesures de sécurité** | Anonymisation NER, HTTPS, pas de logs PII |

## Analyse d'impact (AIPD)

### Risques identifiés

1. **Risque de fuite de PII**
   - **Probabilité :** Faible
   - **Gravité :** Élevée
   - **Mesures :** Anonymisation automatique, pas de stockage
   - **Risque résiduel :** Très faible

2. **Risque d'utilisation abusive**
   - **Probabilité :** Moyenne
   - **Gravité :** Moyenne
   - **Mesures :** Rate limiting, monitoring, alertes
   - **Risque résiduel :** Faible

3. **Risque de faux positifs/négatifs**
   - **Probabilité :** Moyenne
   - **Gravité :** Faible à Moyenne
   - **Mesures :** Modèle ML performant, seuils configurables
   - **Risque résiduel :** Acceptable

### Conclusion AIPD
Les risques résiduels sont acceptables compte tenu des mesures techniques et organisationnelles mises en place.

## Mesures de sécurité techniques

### 1. Sécurité réseau
- ✅ HTTPS/TLS obligatoire en production
- ✅ WAF (Web Application Firewall) recommandé
- ✅ Isolation réseau (VPC/VNET)
- ✅ DDoS protection

### 2. Sécurité applicative
- ✅ Validation des entrées (Pydantic)
- ✅ Limitation de taille des requêtes
- ✅ Rate limiting
- ✅ CORS configuré

### 3. Sécurité des données
- ✅ Anonymisation avant traitement ML
- ✅ Pas de stockage persistant
- ✅ Logs sans PII
- ✅ Chiffrement des secrets

### 4. Monitoring et audit
- ✅ Métriques Prometheus
- ✅ Logs structurés
- ✅ Health checks
- ✅ Alertes en cas d'anomalie

## Procédures en cas de violation

### Détection
- Monitoring continu des logs
- Alertes automatiques sur anomalies
- Revue régulière des métriques

### Notification
En cas de violation de données (peu probable car pas de stockage) :
1. **Notification DPO :** Immédiate
2. **Notification CNIL :** Sous 72h si risque pour les droits
3. **Notification personnes :** Si risque élevé
4. **Documentation :** Registre des violations

### Remédiation
1. Identification de la cause
2. Correction immédiate
3. Évaluation de l'impact
4. Mise à jour des mesures de sécurité

## Conformité par conception (Privacy by Design)

### Principes appliqués

1. **Proactif, pas réactif**
   - Anonymisation dès la conception
   - Pas de stockage par défaut

2. **Vie privée par défaut**
   - Anonymisation activée par défaut
   - Méthode la plus protectrice par défaut

3. **Intégré dans la conception**
   - Pas d'ajout après coup
   - Architecture pensée RGPD-first

4. **Fonctionnalité complète**
   - Pas de compromis performance/confidentialité
   - Protection ET utilité

5. **Sécurité de bout en bout**
   - Protection à chaque couche
   - Défense en profondeur

6. **Visibilité et transparence**
   - Documentation complète
   - Endpoint `/gdpr/compliance`
   - Open source

7. **Respect de l'utilisateur**
   - Contrôle sur l'anonymisation
   - Transparence sur le traitement

## Transferts internationaux

### Hébergement des modèles
- **HuggingFace :** Peut impliquer des transferts hors UE
- **Solution :** Héberger les modèles en Europe si nécessaire
- **Base légale :** Clauses contractuelles types (CCT)

### Recommandations
- Héberger l'API dans l'UE
- Utiliser des fournisseurs cloud certifiés (AWS EU, GCP Europe, Azure Europe)
- Vérifier la localisation des services tiers

## Conformité multilingue

### Documentation
- 🇫🇷 Français (actuelle)
- 🇬🇧 Anglais (fournie)

### Interface API
- Multilingue par défaut
- Support de textes en toute langue

## Contact et responsabilités

### Data Protection Officer (DPO)
- **Email :** dpo@example.com (à configurer)
- **Rôle :** Supervision conformité RGPD

### Responsable technique
- **Email :** tech@example.com (à configurer)
- **Rôle :** Mise en œuvre mesures techniques

### Autorité de contrôle
- **France :** CNIL (Commission Nationale de l'Informatique et des Libertés)
- **Site :** https://www.cnil.fr
- **Contact :** https://www.cnil.fr/fr/plaintes

## Audit et certification

### Auto-évaluation RGPD
- ✅ Minimisation des données
- ✅ Limitation de la conservation
- ✅ Sécurité et confidentialité
- ✅ Transparence
- ✅ Droits des personnes
- ✅ Responsabilité (accountability)

### Recommandations pour certification
- ISO 27001 (Sécurité de l'information)
- ISO 27701 (Privacy Information Management)
- SOC 2 Type II (pour clients US)

## Mises à jour de la conformité

**Version :** 1.0  
**Date :** 2024-11-03  
**Prochaine révision :** 2025-02-03

### Historique
- 2024-11-03 : Version initiale

---

**Note légale :** Ce document est fourni à titre informatif. Chaque organisation utilisant cette API doit effectuer sa propre analyse de conformité RGPD en fonction de son contexte d'utilisation spécifique. Consultation d'un DPO ou avocat spécialisé recommandée.
