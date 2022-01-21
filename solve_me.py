from http.server import BaseHTTPRequestHandler, HTTPServer


class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            self.completed_items = file.readlines()
            file.close()
        except Exception:
            pass

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in sorted(self.current_items.keys()):
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "runserver":
            self.runserver()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def deleteCurrent(self, key):
        self.current_items.pop(key)
        self.write_current()
        self.write_completed()

    def isInCurrent(self, priority):
        return True if priority in self.current_items else False

    def add(self, args):
        args[0] = int(args[0])
        if args[0] in self.current_items:
            key = args[0]
            while key in self.current_items:
                key += 1
            self.current_items[key] = self.current_items[args[0]]
        self.current_items[args[0]] = args[1]
        self.write_current()
        print(f'Added task: \"{str(args[1])}\" with priority {str(args[0])}')

    def done(self, args):
        args[0] = int(args[0])
        if self.isInCurrent(args[0]):
            self.completed_items.append(self.current_items[args[0]])
            self.deleteCurrent(args[0])
            print("Marked item as done.")
        else:
            print(f"Error: no incomplete item with priority {str(args[0])} exists.")

    def delete(self, args):
        args[0] = int(args[0])
        if self.isInCurrent(args[0]):
            self.deleteCurrent(args[0])
            print(f'Deleted item with priority {str(args[0])}')
        else:
            print(f'Error: item with priority {str(args[0])} does not exist. Nothing deleted.')

    def ls(self):
        for n, (key, value) in enumerate(self.current_items.items()):
            print(f'{str(n + 1)}. {value} [{str(key)}]')

    def report(self):
        print(f'Pending : {str(len(self.current_items))}')
        self.ls()
        print(f'\nCompleted : {str(len(self.completed_items))}')
        for n, item in enumerate(self.completed_items):
            print(f'{str(n + 1)}. {item}')

    def tableStyle(self):
        return """
        <!DOCTYPE html>
        <html>
        <body style="background-color:#E6E6FA;">
        <style>
            table {
              border: 1px solid #DA70D6;
              width: 100%;
              padding: 15px;
            }

            th, td {
              text-align: left;
              padding: 8px;
            }

            tr:nth-child(even){background-color: #f2f2f2}
            tr:nth-child(odd){background-color: white}

            th {
              background-color: #DA70D6;
              color: white;
            }
        </style>
        """

    def render_pending_tasks(self):
        self.read_current()
        table_header = """
        <table>
        <caption><h2>Pending Tasks</h2></caption>
            <tr>
                <th>Sr. No.</th>
                <th>Task</th>
                <th>Priority</th>
            </tr>
        """
        table_rows = ""
        for n, (key, value) in enumerate(self.current_items.items()):
            table_rows += f"""
            <tr>
                <td><b>{n + 1}</b></td>
                <td>{value}</td>
                <td>{key}</td>
            </tr>
            """
        return self.tableStyle() + table_header + table_rows + "</table> </body> </html>"


    def render_completed_tasks(self):
        self.read_completed()
        table_header = """
        <table>
        <caption><h2>Completed Tasks</h2></caption>
            <tr>
                <th>Index</th>
                <th>Task</th>
            </tr>
        """
        table_rows = ""
        for n, item in enumerate(self.completed_items):
            table_rows += f"""
            <tr>
                <td><b>{n + 1}</b></td>
                <td>{item}</td>
            </tr>
            """
        return self.tableStyle() + table_header + table_rows + "</table> </body> </html>"


class TasksServer(TasksCommand, BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()
        if self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())
