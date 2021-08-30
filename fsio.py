import logging
from auth import AuthHolder

class FirestoreIO():

    def __init__(self):
        """
        Talks to the firestore database using simplified wrapper functions.

        Functions:\n
        -- -- -- -- -- --
        write_doc(): Write a document
        read_doc(): Read a document
        delete_doc(): Delete a document
        check_exists(): Check if a document exists
        copy_doc(): Copy a document
        read_docs_query(): Searches all docs in a given collection that match a formatted query and returns the matches as a nested dictionary
        """
        self.__auth = AuthHolder()
        self.__firestore = self.__auth.firestore

    def write_doc(self, path, write_dict):
        """
        Write a document to Firestore database. Supports subcollections/docs. Will construct anything that doesn't exist on the way to writing your document.

        :param str path: The path to the object. Ex: "/ExampleCollection/ExampleDocument" Must begin in a / and end without one. Your document name should be at the end of your path.
        :param dict write_dict: This is a dict that will be written as the body of your document.

        :returns: True if we executed the write, False if an error occured on the Firestore write command, None if an error occured locally.
        
        Ex: w_res FirestoreIO.write_doc("/Links/Doc1/SubCollection1/SubCollDoc1", {links: ["https://...", "...", "..."]})
            if w_res is not True:
                print("Error")
        """
        if type(write_dict) is not dict:
            logging.error(f"FirestoreIO: write_doc: type(write_dict) is not dict.")
            return None
        name = self.__is_valid_document_path(path)[1]
        if name is None or name == "" or name == " ":
            logging.error(f"FirestoreIO: write_doc: Invalid document path: {path}")
            return None
        c_handle = self.__make_coll_handle(path)
        if c_handle is None:
            logging.warning("FirestoreIO: write_doc: An issue occured trying to make the collection handle")
        try:
            c_handle.document(name).set(write_dict, merge=True)
            return True
        except Exception as e:
            logging.error(e)
            return False

    def read_doc(self, path):
        """
        Read a document to a dictionary based on doc path. No search, you need to know in advance the documents name and location.
        
        :param str path: The path to your document. Must begin with / and must not end with /. Ex: "/TestCollection/TestDocument" Your doc name must be at the end of your path!

        :returns dict: Your doc's data or None if an error occured or False if the doc didn't exist

        Example Usage: doc_dict = FirestoreIO.read_doc("/TestCollection/TestDocument")
                       if type(doc_dict) is not dict:
                           print("Error")
        """
        name = self.__is_valid_document_path(path)[1]
        if name is None or name == "" or name == " ":
            logging.error(f"FirestoreIO: read_doc: Invalid document path: {path}")
            return None
        c_handle = self.__make_coll_handle(path)
        if c_handle is None:
            logging.error("FirestoreIO: read_doc: An issue occured trying to make the collection handle")
            return None
        try:
            doc = c_handle.document(name).get()
            if(doc.exists):
                return doc.to_dict()
            else:
                logging.warning(f"FirestoreIO: read_doc: Your doc at path: {path} appears to not exist! Check that it exists first and try again!")
                return None
        except Exception as e:
            logging.error(f"FirestoreIO: read_doc: An unknown exception occured trying to read your doc at {path}")
            logging.error(e)
            return None
            
    def check_exists(self, path):
        """
        Check if a document exists at a given path

        :param str path: A valid firestore document path

        :returns boolean: True if exists, False otherwise. Will return None if an error occured.
        """
        doc = self.read_doc(path)
        if type(doc) is not dict:
            return doc
        else:
            return True
        
    def read_docs_by_query(self, collection_path, query_list):
        """Takes the following params to construct and execute a query on all of the Docs in a Collection:

        :param str collection_path: A String formatted path that must start with a / and end with a / (last folder must always be a collection)
        :param list query_list: A list used for formulating the query.

        :returns dict: A dict where the matching Doc id is the key, and the document's Dict is the Doc's dict. Returns None if an error occurred
        
        Example Usage: query_results = FirestoreIO.read_docs_by_query("/ExampleCollection/", ["email", "==", "test@test.net"])
        
        Example Results: {'ExampleMatchingDocName': {'name': 'Bob McFakeName', 'email': 'test@test.net', ...}, {...}, ...}
        """
        c_handle = self.__make_coll_handle(collection_path)
        if c_handle is None:
            logging.error("FirestoreIO: read_docs_by_query: Issue occured making collection handle")
            return None
        q_ref = self.__construct_query_ref(c_handle, query_list)
        if q_ref is None:
            logging.error("FirestoreIO: read_docs_by_query: Issue occured constructing query reference")
            return None
        res = self.__execute_query(q_ref)
        if res is None:
            logging.error("FirestoreIO: read_docs_by_query: Issue occured executing query")
            return None
        return res

    def delete_doc(self, path):
        """
        Delete a document using a valid path.

        :param str path: Valid document path. Must begin but not end in '/'

        :returns: True if document is deleted, False if the document didn't exist, and None if an error has occured.
        """
        exists = self.check_exists(path)
        if exists is False:
            return exists
        elif exists is None:
            return None
        else:
            name = self.__is_valid_document_path(path)[1]
            if name is None or name == "" or name == " ":
                logging.error(f"FirestoreIO: delete_doc: Invalid document path: {path}")
                return None
            c_handle = self.__make_coll_handle(path)
            if c_handle is None:
                logging.error("FirestoreIO: delete_doc: An issue occured while trying to make the collection handle")
                return None
            try:
                c_handle.document(name).delete()
                return True
            except Exception as e:
                logging.error("FirestoreIO: delete_doc: An unknown exception occured tryign to execute firestore delete command")
                logging.error(e)
                return None

    # TODO: Add a recursive copy function
    def copy_doc(self, from_path, to_path):
        """
        Copy a document from point a to point b.
        Will overwrite existing docs at to_path

        :returns: True if success, None if an error has occurreds
        """
        doc = self.read_doc(from_path)
        if type(doc) is not dict:
            logging.error("FirestoreIO: copy_doc: An error occured trying to read doc to copy. Does doc exist?")
            return None
        w_res = self.write_doc(to_path, doc)
        if w_res is not True:
            logging.error("FirestoreIO: copy_doc: An unknown exception occured trying to write document in copy")
            return None
        return True

    def __make_coll_handle(self, path):
        """
        Make a collection hnadle for the write_doc function

        :param str path: Path

        :returns: firestore collection handle made via .collection() or None if err
        """
        path_chopped = self.__is_valid_collection_path(path)[0]
        if path_chopped is None:
            logging.error(f"FirestoreIO: __make_coll_handle: Unable to continue. Path is not valid. Path: {path}")
            return None
        else:
            try:
                coll_handle = self.__firestore.collection(path_chopped)
                return coll_handle
            except Exception as e:
                logging.error(f"FirestoreIO: __make_coll_handle: An unknonw exception occured making a collection handle for path {path}")
                logging.error(e)
                return None

    def __is_valid_document_path(self, path):
        """
        Validates a document path string

        :param str path: Document path

        :returns list of str: [chopped_path, document_name] 

        Document paths must be of type str and begin with a '/' but must not end with a '/' and require an odd number of '/'
        """
        if type(path) != str or path == "" or path == " ":
            logging.error(f"FirestoreIO: __is_valid_document_path: Document path is not string or is an empty string. Your path: {path}")
            return None
        elif path[0] != "/":
            logging.error(f"FirestoreIO: __is_valid_document_path: Document path MUST begin with '/'. Your path: {path}")
            return None
        elif path[-1] == "/":
            logging.error(f"FirestoreIO: __is_valid_document_path: Document path MUST NOT end in '/'. Your path: {path}")
            return None
        else:
            list_slash_pos = []
            counter = 0
            forward_slash_count = 0
            for char in path:
                if char == "/":
                    forward_slash_count += 1
                    list_slash_pos.append(counter)
                counter += 1
            if forward_slash_count % 2 != 0:
                logging.error(f"FirestoreIO: __is_valid_document_path: Path has an odd number of '/'. You are trying to operate on a collection. Your path: {path}")
                return None
            else:
                return [path[1:list_slash_pos[len(list_slash_pos)-1]], path[list_slash_pos[len(list_slash_pos)-1]+1:len(path)]]

    def __is_valid_collection_path(self, path):
        """
        Validates a collection path string

        :param str path: Collection path

        Collection paths must be of type str and begin and end with a '/' and require an even number of '/'
        """
        if type(path) != str or path == "" or path == " ":
            logging.error(f"FirestoreIO: __is_valid_collection_path: Collection path is not string or is an empty string. Your path: {path}")
            return None
        elif path[0] != "/":
            logging.error(f"FirestoreIO: __is_valid_collection_path: Collection path MUST begin with '/'. Your path: {path}")
            return None
        elif path[-1] != "/":
            logging.error(f"FirestoreIO: __is_valid_collection_path: Document path MUST end in '/'. Your path: {path}")
            return None
        else:
            return path[1:len(path)-1]

    def __construct_query_ref(self, collection_handle, query_list):
        """Construct the query reference
           
           :param collection_handle: The collection handle made by __make_collection_handle().
           :param list query_list: A list used for formatting the query.

           :returns: A query reference made with collection_handle.where("", "", "")

           NOTE: If using spaces in your keys (NOT the collection), you must escape them:
           https://stackoverflow.com/a/53048641
        """
        if len(query_list) > 3:
            logging.error("FirestoreIO: __construct_query_ref: You tried to pass a query_list with more than 3 elements")
            return None
        counter = 0
        while counter < len(query_list):
            if isinstance(query_list[counter], str) is False:
                logging.warning("FirestoreIO: __construct_query_ref: You tried to pass something that wasn't a string into your query_list! We will cast for you this time, but please fix it")
                query_list[counter] = str(query_list[counter])
            counter += 1
        try:
            query_ref = collection_handle.where(f'{query_list[0]}', f'{query_list[1]}', f'{query_list[2]}')
            return query_ref
        except Exception as e:
            logging.error("FirestoreIO: __construct_query_ref: An unknown error occured trying to construct your query_ref for you. Please investigate.")
            logging.error(e)
            return None

    def __execute_query(self, query_ref):
        """Execute Firestore read query
           :param query_ref: A query_ref returned by __construct_query_ref()

           :returns dict docs_dicts_dict: Dictionary where keys are doc ids and values are document dictionaries made with doc.to_dict(). If no matches to query, empty. If err, None
        """
        doc_dicts_dict = {}
        docs = None
        try:
            docs = query_ref.stream()
            docs = list(docs)
        except Exception as e:
            logging.error(f"FirestoreIO: __execute_query: An Exception occured while trying to execute your query! Returning None. Stacktrace: \n\n{e}")
            return None
        for doc in docs:
            if str(doc.id) in doc_dicts_dict:
                logging.warning(f"FirestoreIO: __execute_query: Duplicate key in doc_dicts_dict, this is a firestore data structure issue! Will overwrite previous entry!")
                doc_dicts_dict[f'{doc.id}'] = doc.to_dict()
            else:
                doc_dicts_dict[f'{doc.id}'] = doc.to_dict()
        return doc_dicts_dict