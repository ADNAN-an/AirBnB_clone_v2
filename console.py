#!/usr/bin/python3
"""HolbertonBnB console."""
import cmd
import re
from shlex import split
from models import storage
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.place import Place
from models.amenity import Amenity
from models.review import Review


def parse_arguments(arg):
    curly_braces = re.search(r"\{(.*?)\}", arg)
    brackets = re.search(r"\[(.*?)\]", arg)
    if curly_braces is None:
        if brackets is None:
            return [i.strip(",") for i in split(arg)]
        else:
            lexer = split(arg[:brackets.span()[0]])
            return [i.strip(",") for i in lexer] + [brackets.group()]
    else:
        lexer = split(arg[:curly_braces.span()[0]])
        return [i.strip(",") for i in lexer] + [curly_braces.group()]


class HBNBCommand(cmd.Cmd):
    """HolbertonBnB command interpreter.

    Attributes:
        prompt (str): Command prompt.
        supported_classes (set): Set of supported classes.
    """

    prompt = "(hbnb) "
    supported_classes = {"BaseModel", "User", "State", "City", "Place", "Amenity", "Review"}

    def emptyline(self):
        """Do nothing upon receiving an empty line."""
        pass

    def default(self, arg):
        """Default behavior for cmd module when input is invalid."""
        command_dict = {
            "all": self.do_all,
            "show": self.do_show,
            "destroy": self.do_destroy,
            "count": self.do_count,
            "update": self.do_update
        }
        match = re.search(r"\.", arg)
        if match:
            arg_list = [arg[:match.span()[0]], arg[match.span()[1]:]]
            match = re.search(r"\((.*?)\)", arg_list[1])
            if match:
                command = [arg_list[1][:match.span()[0]], match.group()[1:-1]]
                if command[0] in command_dict:
                    call = "{} {}".format(arg_list[0], command[1])
                    return command_dict[command[0]](call)
        print("*** Unknown syntax: {}".format(arg))
        return False

    def do_quit(self, arg):
        """Quit command to exit the program."""
        return True

    def do_EOF(self, arg):
        """EOF signal to exit the program."""
        print("")
        return True

    def do_create(self, arg):
        """Usage: create <class>
        Create a new class instance and print its id.
        """
        arg_list = parse_arguments(arg)
        if not arg_list:
            print("** class name missing **")
        elif arg_list[0] not in HBNBCommand.supported_classes:
            print("** class doesn't exist **")
        else:
            print(eval(arg_list[0])().id)
            storage.save()

    def do_show(self, arg):
        """Usage: show <class> <id> or <class>.show(<id>)
        Display the string representation of a class instance of a given id.
        """
        arg_list = parse_arguments(arg)
        obj_dict = storage.all()
        if not arg_list:
            print("** class name missing **")
        elif arg_list[0] not in HBNBCommand.supported_classes:
            print("** class doesn't exist **")
        elif len(arg_list) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(arg_list[0], arg_list[1]) not in obj_dict:
            print("** no instance found **")
        else:
            print(obj_dict["{}.{}".format(arg_list[0], arg_list[1])])

    def do_destroy(self, arg):
        """Usage: destroy <class> <id> or <class>.destroy(<id>)
        Delete a class instance of a given id."""
        arg_list = parse_arguments(arg)
        obj_dict = storage.all()
        if not arg_list:
            print("** class name missing **")
        elif arg_list[0] not in HBNBCommand.supported_classes:
            print("** class doesn't exist **")
        elif len(arg_list) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(arg_list[0], arg_list[1]) not in obj_dict:
            print("** no instance found **")
        else:
            del obj_dict["{}.{}".format(arg_list[0], arg_list[1])]
            storage.save()

    def do_all(self, arg):
        """Usage: all or all <class> or <class>.all()
        Display string representations of all instances of a given class.
        If no class is specified, displays all instantiated objects."""
        arg_list = parse_arguments(arg)
        if arg_list and arg_list[0] not in HBNBCommand.supported_classes:
            print("** class doesn't exist **")
        else:
            obj_list = []
            for obj in storage.all().values():
                if arg_list and arg_list[0] == obj.__class__.__name__:
                    obj_list.append(obj.__str__())
                elif not arg_list:
                    obj_list.append(obj.__str__())
            print(obj_list)

    def do_count(self, arg):
        """Usage: count <class> or <class>.count()
        Retrieve the number of instances of a given class."""
        arg_list = parse_arguments(arg)
        count = 0
        for obj in storage.all().values():
            if arg_list and arg_list[0] == obj.__class__.__name__:
                count += 1
        print(count)

    def do_update(self, arg):
        """Usage: update <class> <id> <attribute_name> <attribute_value> or
       <class>.update(<id>, <attribute_name>, <attribute_value>) or
       <class>.update(<id>, <dictionary>)
        Update a class instance of a given id by adding or updating
        a given attribute key/value pair or dictionary."""
        arg_list = parse_arguments(arg)
        obj_dict = storage.all()

        if not arg_list:
            print("** class name missing **")
            return False
        if arg_list[0] not in HBNBCommand.supported_classes:
            print("** class doesn't exist **")
            return False
        if len(arg_list) == 1:
            print("** instance id missing **")
            return False
        if "{}.{}".format(arg_list[0], arg_list[1]) not in obj_dict.keys():
            print("** no instance found **")
            return False
        if len(arg_list) == 2:
            print("** attribute name missing **")
            return False
        if len(arg_list) == 3:
            try:
                type(eval(arg_list[2])) != dict
            except NameError:
                print("** value missing **")
                return False

        if len(arg_list) == 4:
            obj = obj_dict["{}.{}".format(arg_list[0], arg_list[1])]
            if arg_list[2] in obj.__class__.__dict__.keys():
                val_type = type(obj.__class__.__dict__[arg_list[2]])
                obj.__dict__[arg_list[2]] = val_type(arg_list[3])
            else:
                obj.__dict__[arg_list[2]] = arg_list[3]
        elif type(eval(arg_list[2])) == dict:
            obj = obj_dict["{}.{}".format(arg_list[0], arg_list[1])]
            for k, v in eval(arg_list[2]).items():
                if (k in obj.__class__.__dict__.keys() and
                        type(obj.__class__.__dict__[k]) in {str, int, float}):
                    val_type = type(obj.__class__.__dict__[k])
                    obj.__dict__[k] = val_type(v)
                else:
                    obj.__dict__[k] = v
        storage.save()


if __name__ == "__main__":
    HBNBCommand().cmdloop()
