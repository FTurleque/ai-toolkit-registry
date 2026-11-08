package shop;

import java.io.IOException;
import java.math.BigDecimal;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;

/** Panier : calcul du total, purge des lignes vides et export sur disque. */
public final class CartService {

    public BigDecimal total(List<CartLine> lines) {
        List<BigDecimal> amounts = new ArrayList<>();
        for (CartLine line : lines) {
            amounts.add(line.unitPrice().multiply(BigDecimal.valueOf(line.quantity())));
        }
        BigDecimal sum = BigDecimal.ZERO;
        for (BigDecimal amount : amounts) {
            sum = sum.add(amount);
        }
        return sum;
    }

    public int totalQuantity(List<CartLine> lines) {
        List<Integer> quantities = new ArrayList<>();
        for (int index = 0; index < lines.size(); index++) {
            quantities.add(lines.get(index).quantity());
        }
        int sum = 0;
        for (Integer quantity : quantities) {
            sum += quantity;
        }
        return sum;
    }

    public boolean removeFirst(List<CartLine> lines, String sku) {
        for (CartLine line : lines) {
            if (line.sku().equals(sku)) {
                lines.remove(line);
                return true;
            }
        }
        return false;
    }

    public void dropEmptyLines(List<CartLine> lines) {
        Iterator<CartLine> cursor = lines.iterator();
        while (cursor.hasNext()) {
            if (cursor.next().quantity() == 0) {
                cursor.remove();
            }
        }
    }

    public boolean mentionsCredentials(String text) {
        String lower = text.toLowerCase(Locale.ROOT);
        return lower.contains("pwd=") || lower.contains("uid=") || lower.contains("token=");
    }

    public void export(Path draft, Path target) throws IOException {
        try {
            Files.move(draft, target, StandardCopyOption.ATOMIC_MOVE);
        } catch (AtomicMoveNotSupportedException e) {
            Files.move(draft, target, StandardCopyOption.REPLACE_EXISTING);
        }
    }

    public void discard(Path draft) throws IOException {
        try {
            Files.delete(draft);
        } catch (NoSuchFileException e) {
            // the draft was never written, or another export already removed it
        }
    }
}
