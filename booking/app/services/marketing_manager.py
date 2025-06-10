

class MarketingManager:
    _instance = None
    _initialized = False

    # Data structure:
    #   {
    #     "user_id": number,
    #   }
    data = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarketingManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not MarketingManager._initialized:
            MarketingManager._initialized = True

    def notify_all(self, message):
        for user in self.data:
            print(f"Sending message to user {user['user_id']}: {message}")

    def subscribe(self, user_id):
        self.data.append({
            "user_id": user_id
        })
        print(f"Subscribed user {user_id} to marketing notifications")

    def unsubscribe(self, user_id):
        self.data = [d for d in self.data if d["user_id"] != user_id]
        print(f"Unsubscribed user {user_id} from marketing notifications")

        


