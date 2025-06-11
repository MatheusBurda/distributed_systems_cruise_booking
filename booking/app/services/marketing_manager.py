

class MarketingManager:
    _instance = None
    _initialized = False

    # Data structure:
    #   [
    #     "user_id": number,
    #   ]
    data = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarketingManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not MarketingManager._initialized:
            MarketingManager._initialized = True

    def notify_all(self, message):
        notified = 0
        for user in self.data:
            print(f"Sending message to user {user}: {message}")
            notified += 1

        return notified


    def subscribe(self, user_id):
        if user_id in self.data:
            print(f"User {user_id} already subscribed to marketing notifications")
            return
        
        self.data.append(user_id)
        print(f"Subscribed user {user_id} to marketing notifications")

    def unsubscribe(self, user_id):
        if user_id not in self.data:
            print(f"User {user_id} is not subscribed to marketing notifications")
            return
        
        self.data = [d for d in self.data if d != user_id]
        print(f"Unsubscribed user {user_id} from marketing notifications")

