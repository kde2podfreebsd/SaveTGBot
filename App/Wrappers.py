def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

# def markupLanguage(func):
#
#     def wrapper(*args, **kwargs):
#         func(*args, **kwargs)
#
#     return wrapper
