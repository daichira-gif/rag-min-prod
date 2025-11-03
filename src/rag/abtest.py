import hashlib

def bucket_for_user(user_key: str, default_bucket: str = "A") -> str:
    if not user_key:
        return default_bucket
    h = hashlib.sha256(user_key.encode("utf-8")).hexdigest()
    # 50/50 split
    return "A" if int(h[:2], 16) < 128 else "B"
