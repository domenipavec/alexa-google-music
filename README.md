# alexa-google-music
Play google music with amazon alexa

**alexa-google-music is not supported nor endorsed by Google.**

## Setup

### Alexa skill

Create new alexa skill at https://developer.amazon.com/edw/home.html

Select that the skill uses Audio Player

Use this intent schema:
```
{
    "intents": [
        {
            "intent": "AMAZON.PauseIntent"
        },
        {
            "intent": "AMAZON.ResumeIntent"
        },
        {
            "intent": "AMAZON.NextIntent"
        },
        {
            "intent": "AMAZON.PreviousIntent"
        },
        {
            "intent": "AMAZON.PlaybackAction<object@MusicPlaylist>"
        },
      	{
          	"intent": "SayHiIntent"
        }
    ]
}
```

And sample utterances (SayHiIntent is there because one custom intent is needed):
```
SayHiIntent say hi
```

### Dynamodb

Create new table in Dynamodb in aws console

### Lambda

Create new lambda function. Add permissions for Dynamodb to lambda role.

Modify *lambda.json* and *settings.py* with correct information. Use application password for
google if you use 2FA.

Use lambda-uploader to upload lambda:
`lambda-uploader .`
