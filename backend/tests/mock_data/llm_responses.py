ACTION_ITEMS_RESPONSE = """
{
  "items": [
    {
      "action": "Créer la page de login avec OAuth Google",
      "assigned_to": "Marc",
      "deadline": "Jeudi",
      "priority": "Haute",
      "context": "Discussion sur l'authentification utilisateur"
    },
    {
      "action": "Configurer la base de données PostgreSQL",
      "assigned_to": "Sarah",
      "deadline": "Aujourd'hui",
      "priority": "Haute",
      "context": "Choix de la base de données pour le MVP"
    },
    {
      "action": "Développer l'API principale",
      "assigned_to": "Speaker 1",
      "deadline": "Vendredi",
      "priority": "Moyenne",
      "context": "Architecture backend du projet"
    }
  ]
}
"""

DECISIONS_RESPONSE = """
{
  "items": [
    {
      "decision": "Utiliser PostgreSQL comme base de données",
      "reasoning": "Meilleure intégration avec l'ORM actuel",
      "timestamp": "00:12:45"
    }
  ]
}
"""

QUESTIONS_RESPONSE = """
{
  "items": [
    {
      "question": "PostgreSQL ou MongoDB ?",
      "asked_by": "Speaker 3",
      "context": "Discussion sur le choix de la base de données",
      "timestamp": "00:10:30"
    }
  ]
}
"""

SUMMARY_RESPONSE = """
{
  "full_markdown": "# Compte rendu\\n\\nDécisions prises et actions assignées."
}
"""
