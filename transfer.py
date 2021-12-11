#!/usr/bin/python

import mysql.connector
import sys
import json

def export_char(account_name, character_name):

    def fetch_data(account_name, character_name):
        cursor.execute("""
            SELECT * FROM darkflameserver.charinfo ci 
            JOIN darkflameserver.accounts a 
            WHERE a.name = LOWER(%s) and ci.name = LOWER(%s) and ci.account_id = a.id""", 
            [account_name.lower(), character_name.lower()]
        )
        charinfo = cursor.fetchone()
        character_id = charinfo[0]

        cursor.execute("SELECT xml_data FROM darkflameserver.charxml WHERE id = %s", [character_id])
        xml_data = cursor.fetchone()[0]

        cursor.execute("SELECT * FROM darkflameserver.properties WHERE owner_id = %s", [character_id])
        properties = cursor.fetchall()

        cursor.execute("SELECT id FROM darkflameserver.properties WHERE owner_id = %s", [character_id])
        property_ids_result = cursor.fetchall()
        property_ids = []
        for row in property_ids_result:
            property_ids.append(str(row[0]))

        properties_contents = []
        if property_ids:
            cursor.execute("SELECT * FROM darkflameserver.properties_contents WHERE property_id in ({id})".format(id=", ".join(property_ids)))
            properties_contents = cursor.fetchall()

        return { 'charinfo': charinfo, 'xml_data': xml_data, 'properties': properties, 'properties_contents': properties_contents }

    char_data = fetch_data(account_name, character_name)
    f = open(str(char_data['charinfo'][0])+'.json', "w")
    f.write(json.dumps(char_data, default=str))
    f.close()

    return


def import_char(account_name, filepath):

    def create_rows(account_id, char_data):
        cursor.execute("SELECT MAX(id) FROM darkflameserver.charinfo")
        new_char_id = cursor.fetchone()[0] + 1

        ci = char_data['charinfo']
        cursor.execute(
            """INSERT INTO darkflameserver.charinfo (id, account_id, name, pending_name, needs_rename, last_login, permission_map) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            [new_char_id, account_id, ci[2], ci[3], ci[4], ci[6], ci[7]]
        )
        db.commit()

        cursor.execute(
            """INSERT INTO darkflameserver.charxml (id, xml_data) 
            VALUES (%s, %s)""",
            [new_char_id, char_data['xml_data']]
        )
        db.commit()

        for row in char_data['properties']:
            cursor.execute(
                """INSERT INTO darkflameserver.properties (id, owner_id, template_id, clone_id, name, description, rent_amount, rent_due, privacy_option, mod_approved, last_updated, time_claimed, rejection_reason, reputation, zone_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                [row[0], new_char_id, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]]
            )
            db.commit()

        for row in char_data['properties_contents']:
            cursor.execute(
                """INSERT INTO darkflameserver.properties_contents (id, property_id, ugc_id, lot, x, y, z, rx, ry, rz, rw) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]]
            )
            db.commit()

        return

    f = open(filepath, "r")
    text = f.read()
    f.close()
    char_data = json.loads(text)

    cursor.execute("SELECT id FROM darkflameserver.accounts WHERE name = LOWER(%s)", [account_name.lower()])
    account_id = cursor.fetchone()[0]

    create_rows(account_id, char_data)

    return


if __name__ == '__main__':

    db = mysql.connector.connect(
        host = "your_db_host",
        user = "your_db_user",
        password = "your_db_pass",
        port = 3306
    )
    cursor = db.cursor(prepared=True)

    if sys.argv[1] not in ['import', 'export', 'i', 'e']:
        print('argument 1 must be "import" or "export"')
        sys.exit(2)

    if sys.argv[1] in ['export', 'e']:
        export_char(sys.argv[2], sys.argv[3])
    else:
        import_char(sys.argv[2], sys.argv[3])
