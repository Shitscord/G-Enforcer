# Genforcer
An enforcer robot for the G channel

In order for the bot to run you must have a config file in the script directory `data/config.json`.

Should contain the attributes:
```json
{
  "description":"Whatever you want",
  "token":"Bot user token here",
  "character_ratio": 0.75 // A float from 0 to 1 that represents what percent of characters in a message must be "G".
}
```
