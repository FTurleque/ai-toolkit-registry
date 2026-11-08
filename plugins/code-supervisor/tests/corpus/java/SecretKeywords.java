class SecretKeywords {
  boolean looksSensitive(String text) {
    String lower = text.toLowerCase();
    return lower.contains("pwd=") || lower.contains("uid=") || lower.contains("token=");
  }

  String afterApostrophe() {
    log("can't reach the vault"); String password = "K7#mq2vZ";
    return password;
  }

  void log(String message) { }
}
