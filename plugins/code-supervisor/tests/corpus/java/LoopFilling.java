import java.util.ArrayList;
import java.util.List;
import java.util.Map;

class LoopFilling {
  int fillThenRead(int count) {
    List<Integer> squares = new ArrayList<>();
    for (int i = 0; i < count; i++) {
      squares.add(i * i);
    }
    int sum = 0;
    for (Integer square : squares) {
      sum += square;
    }
    return sum;
  }

  List<String> copyThenClear(List<String> names) {
    List<String> trimmed = new ArrayList<>();
    for (String name : names) {
      trimmed.add(name.trim());
    }
    names.clear();
    return trimmed;
  }

  void dropWhileIterating(List<String> names) {
    for (String name : names) {
      if (name.isEmpty()) {
        names.remove(name);
      }
    }
  }

  void growOnOneLine(List<String> names) {
    for (String name : names) names.add(name + "!");
  }

  void dropAllman(List<String> names)
  {
    for (String name : names)
    {
      names.remove(name);
    }
  }

  void removeThenStop(List<String> names, String target) {
    for (String name : names) {
      if (name.equals(target)) {
        names.remove(name);
        break;
      }
    }
  }

  void growEntries(Map<String, Integer> counts) {
    for (final Map.Entry<String, Integer> entry : counts.entrySet()) {
      counts.put(entry.getKey() + "!", entry.getValue());
    }
  }

  void growAll(List<String> names, List<String> extra) {
    for (String name : names) {
      names.addAll(extra);
    }
  }
}
