# lego-universe-save-transfer

This Python script allows you to export all the data associated with a character in the database into a JSON file, and then load it into any other system.

Before running, make sure to update the transfer.py file with the correct database credentials at the bottom.

**To export a character:**
Include as an argument the name of the account (name field from accounts table) and name of the character (name field from charinfo table)
`transfer.py export {account_name} {character_name}`


**To import a character:**
Include as an argument the name of the account (name field from account table) and a path to the JSON export file
`transfer.py import {account_name} {path_to_file}`
