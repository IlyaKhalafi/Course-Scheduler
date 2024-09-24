class Teacher:
    insurance = 1500
    def __init__(self, name, knowledge, salary, max_class, accessibility, dummy):
        self.name = name
        self.knowledge = knowledge
        self.salary = salary
        self.max_class = max_class
        self.accessibility = accessibility
        self.dummy = dummy # This is a flag to indicate whether this teacher is a real teacher

class Class:
    def __init__(self, code, course, students_count, sessions):
        self.code = code
        self.course = course
        self.students_count = students_count
        self.sessions = sessions  

class Course:
    def __init__(self, title, level, fee):
        self.title = title
        self.level = level
        self.fee = fee
