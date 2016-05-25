import logging 
import argparse
import psycopg2
# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established.")

def put(name, snippet, hide, unhide):
    """
    Store a snippet with an associated name.

    Returns the name and the snippet
    """
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
    with connection, connection.cursor() as cursor:
        command = "Insert into snippets values (%s, %s)"
        try:
            command = "insert into snippets values (%s, %s, %s)"
            cursor.execute(command, (name, snippet, hide))
        except psycopg2.IntegrityError as e:
            connection.rollback()
            command = "update snippets set message=%s, hidden=%s where keyword=%s"
            cursor.execute(command, (snippet, hide, name))
    connection.commit()
    logging.debug("Snippet stored successfully.")
    return name, snippet
    
    
def get(name):
    """Retrieve the snippet with a given name.

    If there is no such snippet, return '404: Snippet Not Found'.

    Returns the snippet.
    """
    with connection, connection.cursor() as cursor:
        command = "select message from snippets where keyword=%s"
        cursor.execute(command, (name,))
        row = cursor.fetchone()
    logging.error("Snippet retrieved.")
    return row
    
def search(string):
    """Find a string in snippets
    """
    with connection, connection.cursor() as cursor:
        command = "Select keyword from snippets where keyword like '%{}%' and not hidden".format(string)
        cursor.execute(command)
        c = cursor.fetchall()
    connection.commit()
    logging.error("Strings found")
    return c
    
def catalog():
    """Retrieves list of tuples of all the keywords.
    """
    with connection, connection.cursor() as cursor:
        cursor.execute("select keyword, message from snippets where not hidden order by keyword") 
        d = cursor.fetchall()
    connection.commit()
    logging.error("Keyword catalog retrieved")
    return d

def main():
    """Main function"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="Name of the snippet")
    put_parser.add_argument("snippet", help="Snippet text")
    put_parser.add_argument("--hide", help="Flags snippet as hidden", action='store_true', default=False)
    put_parser.add_argument("--unhide", help="Removes hidden flag on snippet", action='store_false', default=False)
    
    # Subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="Name of the snippet")
    
    # Subparser for the catalog command
    logging.debug("Constructing catalog subparser")
    catalog_parser = subparsers.add_parser("catalog", help="Look up snippets by keyword")
    
    #Subparser for the search command
    logging.debug("Constructing catalog subparser")
    search_parser = subparsers.add_parser("search", help="Find string in snippets")
    search_parser.add_argument("string", help="String searched")
    
    arguments = parser.parse_args()
    
    # Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")

    if command == "put":
        name, snippet = put(**arguments)
        print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)
        if snippet == None:
            print("404 Error: Snippet Not Found")
        else:
            print("Retrieved snippet: {!r}".format(snippet))
    elif command == "catalog":
        snippet = catalog()
        print("Keywords: {!r}".format(snippet))
    elif command == "search":
        snippet = search(**arguments)
        print("Snippets with string: {!r}".format(snippet))
        
if __name__ == "__main__":
    main()
    
