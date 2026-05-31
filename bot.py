import telebot
import gspread

# بيانات الاعتماد الكاملة
CREDENTIALS_DICT = {
  "type": "service_account",
  "project_id": "rare-mechanic-466808-s2",
  "private_key_id": "52b5890bec4b761f97bec22f635c7bcbcf579713",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDo0Tbc5msNoXEN\nA10lOWFNYGki9xXYXBmhma68h/AIzFENKr8Mzx5JNBPaONAlB9dsnVRMFM/eMwlr\nPy+Hf2UFgB8eXrxIRy3JNl97K+cwm2C+RQXMqUSBYGOEyfsbskhSgicnsVMykGtV\nSthJdJ1/yUwi8fk4y4DSIQAeBqe9f2ncy51TEF92LAUpNArrz+9JIK+nFJFnF+tI\nP3TZVctQUf+dxpDv74WIrjsHAsq1xKqGvlo9N8O3B8LVANgA8UlDS802cNp2VUW3\nNu/6KW7iCwO/5KtZQln4T0uKMU4CCM4L+pLJmlvckHmaJiu7Fo7ewdw5pRpkc5Hc\nYQqjFLbFAgMBAAECggEAIpAOmkAtw94D87fcX96TGqLVsN5oFJDlsDcpuOzgXloA\rVj7eFoWJ61uxg55ngm6OjJoFYxgaJ8AhragZnfr5iNlW0OapYtFmZG0Hou/vFhQ\nxiZmjEHTvPYzh/7ZQ70VngQa7npVfNPyTzz3e34vtI0Me8Ka6krR0sAZ7Zs00z16\n1ZJBAz8iyXLSaozFcKz699CQDhkpBniGPp1qRsiDDdAIHsnCOosinEjLkxtYHVPh\nQhA/t5fSSnfDiez8cy7uJYo4LK0wSJCP4Z2Lgj74tTgl3Z+DNE+3uSAVy9gklboL\ngbxLS93tF7sA59jGJPY0mp7ofFmHxblQt3Kt6RctqQKBgQD6qDjsQr9TNc0sZJva\naALAm6pOYxharwYzqOJvYwAriZHirCJMdvebvLqty0nIeH24kDN3HoYtqxaGWwrP\nrtoFJuX3dtxASrCDFteasGeP0DwNV1DYuUHuRCFnZ6VT2qZpicOsbU0W+LoGN70G\nDm09/7IW6Xa3djrgYSD2LlErTQKBgQDtx6TWo0mHOGNtvTBu8UNhZnAWj3aYmQTu\nK8naMV5e5rKyDEQ0/i22JcVxYln4FbdxDbDQ0uL6QaT+8JpiEV2SGgh/y4eoVvHZ\nt644l+YrqPNiHHjUrOjxS8oyDD+lkBkFWVmV2NAYcAjFBclMrSigc4JigolAzaGY\niXSGNfDNWQKBgHaaVqTkSGd1E6onyN8lS/gbMBB7LzDplEOpa8tMyu3O4GqjDG+l\n8y+Ls8E8aaMj8Ej+YnvAw7ikNbpJJepzT9IUP8hCQ6FgNfkxO7+ELNyNqXyejjCe\nKCY3sp6dGkt9MDTL7PyPk2SFOHBsu1I8TVCCxp+0xGm21dEJ5HDYJawZAoGBANaC\nPBgSWPvvB+vxOCdt6h6NXmNL627A5OzEfiYkUYGF2AG+BS5VfAGN07B1TLr9RG9u\nLWxGQ9QGsoX3ox8DkYmDiNVZVLmuLiL+jOKrTk9m7KI/E1ax4rgEapV57VU8SQZF\nVAdWAG17bL3peW9961/MtPyPzKi0marVnlSRhvqJAoGBALIdA1I3/YAh9JMpzWqD\nSG8QQ6g/yEMcL1f0nzJSxOaTuX50mxYQu6x4/hK+869t4QDDFlR2OPpa25OvMJGp\nLn+j3bdxRB2sDbU0V+jXhP9OEC9ftzZ7lztmPAvWaMXwJwJNUvziCfI4uWpSoZCf\nSF0CSDFAwwRrl9bY2SDGjBHk\n-----END PRIVATE KEY-----",
  "client_email": "general-bot-service@rare-mechanic-466808-s2.iam.gserviceaccount.com",
  "token_uri": "https://oauth2.googleapis.com/token"
}

gc = gspread.service_account_from_dict(CREDENTIALS_DICT)
sh = gc.open("General_Bot_Data")

BOT_TOKEN = "8606943008:AAGcFvCT73iHY71OOhkw2USy8bNMki72g8s"
bot = telebot.TeleBot(BOT_TOKEN)

# ... (بقية أوامر البوت كما هي)
bot.infinity_polling()
