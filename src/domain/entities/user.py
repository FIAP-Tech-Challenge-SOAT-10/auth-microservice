class User:
    """
    User entity representing a system user.
    """
    def __init__(self, id: int, username: str, full_name: str, cpf: str, email: str, password_hash: str):
        self.id = id
        self.username = username
        self.full_name = full_name
        self.cpf = cpf
        self.email = email
        self.password_hash = password_hash

    def __repr__(self):
        return f"User(name={self.full_name}, cpf={self.cpf}, email={self.email})"
