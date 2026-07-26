"""A user service module with missing input validation."""

from dataclasses import dataclass


@dataclass
class User:
    name: str
    email: str
    age: int


def create_user(name: str, email: str, age: int) -> User:
    # Bug: no validation on email format or age range
    return User(name=name, email=email, age=age)


def get_user_display(user: User) -> str:
    return f"{user.name} <{user.email}>"


def get_users_by_age(users: list[User], min_age: int) -> list[User]:
    # Bug: should also validate min_age is non-negative
    return [u for u in users if u.age >= min_age]


if __name__ == "__main__":
    user = create_user("Alice", "not-an-email", -5)
    print(f"Created user: {get_user_display(user)}")
