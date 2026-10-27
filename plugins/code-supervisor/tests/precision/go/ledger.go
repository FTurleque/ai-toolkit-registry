package ledger

import (
	"database/sql"
	"errors"
	"fmt"
)

// Entry is one movement on an account.
type Entry struct {
	Account string
	Cents   int64
}

// Store persists ledger entries with bound parameters only.
type Store struct {
	db *sql.DB
}

// ErrUnknownAccount is returned when an account has no entry.
var ErrUnknownAccount = errors.New("unknown account")

// Append records an entry.
func (s *Store) Append(e Entry) error {
	_, err := s.db.Exec("INSERT INTO entries(account, cents) VALUES (?, ?)", e.Account, e.Cents)
	if err != nil {
		return fmt.Errorf("cannot update ledger for %s: %w", e.Account, err)
	}
	return nil
}

// Balance sums the entries of an account.
func (s *Store) Balance(account string) (int64, error) {
	var total sql.NullInt64
	err := s.db.QueryRow("SELECT SUM(cents) FROM entries WHERE account = ?", account).Scan(&total)
	if err != nil {
		return 0, fmt.Errorf("cannot read balance of %s: %w", account, err)
	}
	if !total.Valid {
		return 0, ErrUnknownAccount
	}
	return total.Int64, nil
}

// Average returns the mean movement, or zero for an empty list.
func Average(entries []Entry) float64 {
	if len(entries) == 0 {
		return 0
	}
	var sum int64
	for _, e := range entries {
		sum += e.Cents
	}
	return float64(sum) / float64(len(entries))
}
