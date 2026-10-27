import java.sql.SQLException;
import java.sql.Statement;

class SqlMessages {
  String failureMessage(long orderId) {
    return "Cannot update order " + orderId;
  }

  String twoLiterals() {
    return "INSERT INTO audit(id, at) VALUES (?, ?) " + "ON CONFLICT DO NOTHING";
  }

  String inList(String placeholders) {
    return "SELECT id FROM item WHERE id IN (" + placeholders + ")";
  }

  void direct(Statement st, String name) throws SQLException {
    st.executeQuery("SELECT * FROM users WHERE name = '" + name + "'");
  }
}
