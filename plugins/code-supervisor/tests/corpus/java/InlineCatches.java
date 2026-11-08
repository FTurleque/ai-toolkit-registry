import java.io.IOException;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

class InlineCatches {
  Object rethrow(String s) {
    try { return parse(s); } catch (IllegalStateException e) { throw new RuntimeException(e); }
  }

  Integer silentNull(String s) {
    try { return Integer.valueOf(s); } catch (NumberFormatException e) { return null; }
  }

  void fallbackMove(Path from, Path to) throws IOException {
    try { Files.move(from, to, StandardCopyOption.ATOMIC_MOVE); } catch (AtomicMoveNotSupportedException e) { Files.move(from, to); }
  }

  void reallyEmpty(String s) {
    try { parse(s); } catch (RuntimeException e) { }
  }

  void shortComment(Path p) throws IOException {
    try {
      Files.delete(p);
    } catch (NoSuchFileException e) {
      // already gone
    }
  }

  Object parse(String s) { return s; }
}
