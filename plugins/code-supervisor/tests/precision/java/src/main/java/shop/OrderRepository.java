package shop;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

/** Lecture et ecriture des commandes, toujours par requetes parametrees. */
public final class OrderRepository {

    private static final String INSERT_ORDER =
            "INSERT INTO orders(id, customer_id, status) VALUES (?, ?, ?) "
                    + "ON CONFLICT (id) DO NOTHING";
    private static final int LOOKUP_SLICE = 50;

    private final Connection connection;

    public OrderRepository(Connection connection) {
        this.connection = connection;
    }

    public void save(Order order) {
        try (PreparedStatement statement = connection.prepareStatement(INSERT_ORDER)) {
            statement.setString(1, order.id());
            statement.setString(2, order.customerId());
            statement.setString(3, order.status().name());
            statement.executeUpdate();
        } catch (SQLException e) { throw new StorageException("Cannot update order " + order.id(), e); }
    }

    public Optional<Order> find(String id) {
        try (PreparedStatement statement = connection.prepareStatement(
                "SELECT id, customer_id, status FROM orders WHERE id = ?")) {
            statement.setString(1, id);
            try (ResultSet rows = statement.executeQuery()) {
                return rows.next() ? Optional.of(read(rows)) : Optional.empty();
            }
        } catch (SQLException e) {
            throw new StorageException("Cannot read order " + id, e);
        }
    }

    public List<Order> findAll(List<String> ids) {
        String placeholders = String.join(", ", Collections.nCopies(LOOKUP_SLICE, "?"));
        String sql = "SELECT id, customer_id, status FROM orders WHERE id IN (" + placeholders + ")";
        List<Order> found = new ArrayList<>();
        for (int from = 0; from < ids.size(); from += LOOKUP_SLICE) {
            List<String> slice = ids.subList(from, Math.min(ids.size(), from + LOOKUP_SLICE));
            found.addAll(querySlice(sql, slice));
        }
        return found;
    }

    private List<Order> querySlice(String sql, List<String> slice) {
        List<Order> orders = new ArrayList<>();
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            for (int index = 0; index < LOOKUP_SLICE; index++) {
                statement.setString(index + 1, index < slice.size() ? slice.get(index) : null);
            }
            try (ResultSet rows = statement.executeQuery()) {
                while (rows.next()) {
                    orders.add(read(rows));
                }
            }
        } catch (SQLException e) {
            throw new StorageException("Cannot read orders", e);
        }
        return orders;
    }

    private static Order read(ResultSet rows) throws SQLException {
        return new Order(rows.getString("id"), rows.getString("customer_id"),
                OrderStatus.valueOf(rows.getString("status")));
    }
}
