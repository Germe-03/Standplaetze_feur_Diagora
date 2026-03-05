

class Campaign:
    def __init__(self, campaign_id, name, year, budget, user_id, is_active=True):
        self.__campaign_id = campaign_id
        self.__name = name
        self.__year = year
        self.__budget = budget
        self.__user_id = user_id
        self.__is_active = bool(is_active)

    def __repr__(self):
        return (f"Campaign(id={self.__campaign_id!r}, Name={self.__name!r}, Year={self.__year!r}"
                f"budget={self.__budget!r}), User ID={self.__user_id!r}, is_active={self.__is_active!r}")


    @property
    def campaign_id(self):
        return self.__campaign_id

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        if not name:
            raise ValueError("Name is required")
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        self.__name = name

    @property
    def year(self):
        return self.__year

    @year.setter
    def year(self, year):
        if not year:
            raise ValueError("Year is required")
        if not isinstance(year, int):
            raise TypeError("Year must be a int")
        self.__year = year

    @property
    def budget(self):
        return self.__budget

    @budget.setter
    def budget(self, budget):
        if budget is None:
            raise ValueError("Budget is required")
        if not isinstance(budget, (int, float)):
            raise TypeError("Budget must be a number")
        self.__budget = float(budget)

    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, user_id):
        if not user_id:
            raise ValueError("User ID is required")
        if not isinstance(user_id, int):
            raise TypeError("User ID must be a Integer")
        self.__user_id = user_id

    @property
    def is_active(self):
        return self.__is_active

    @is_active.setter
    def is_active(self, is_active):
        self.__is_active = bool(is_active)
