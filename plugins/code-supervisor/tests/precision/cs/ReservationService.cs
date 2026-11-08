using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;

namespace Booking
{
    public sealed class ReservationService
    {
        private const string InsertReservation =
            "INSERT INTO reservations(id, room, night) VALUES (@id, @room, @night) " +
            "ON CONFLICT DO NOTHING";

        private readonly IDbConnection _connection;

        public ReservationService(IDbConnection connection)
        {
            _connection = connection;
        }

        public void Reserve(Guid id, string room, DateTime night)
        {
            using var command = _connection.CreateCommand();
            command.CommandText = InsertReservation;
            AddParameter(command, "@id", id);
            AddParameter(command, "@room", room);
            AddParameter(command, "@night", night.Date);
            try { command.ExecuteNonQuery(); } catch (DataException e) { throw new InvalidOperationException("Cannot update reservation " + id, e); }
        }

        public IReadOnlyList<string> FreeRooms(IEnumerable<string> rooms, ISet<string> booked)
        {
            var free = new List<string>();
            foreach (var room in rooms)
            {
                if (!booked.Contains(room))
                {
                    free.Add(room);
                }
            }
            return free;
        }

        public double OccupancyRate(int booked, int capacity)
        {
            if (capacity == 0)
            {
                return 0;
            }
            return (double)booked / capacity;
        }

        public string Summary(IEnumerable<string> rooms) =>
            string.Join(", ", rooms.OrderBy(room => room, StringComparer.Ordinal));

        private static void AddParameter(IDbCommand command, string name, object value)
        {
            var parameter = command.CreateParameter();
            parameter.ParameterName = name;
            parameter.Value = value;
            command.Parameters.Add(parameter);
        }
    }
}
