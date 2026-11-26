using System.Data.Common;
using System.Text;
using System.Text.Json;
using Microsoft.AnalysisServices.AdomdClient;

// Internal reader process. The Python gateway authorizes the exact model and
// read-only DAX before launching this process. Tokens arrive only on stdin.
static string Connection(string workspace, string model, int timeout)
{
    var builder = new DbConnectionStringBuilder();
    builder["Data Source"] = "powerbi://api.powerbi.com/v1.0/myorg/" + Uri.EscapeDataString(workspace);
    builder["Initial Catalog"] = model;
    builder["Connect Timeout"] = timeout;
    return builder.ConnectionString;
}

try
{
    if (args.Length == 1 && args[0] == "--self-test")
    {
        // Offline image check: load the actual ADOMD assembly on this runtime.
        using var test = new AdomdConnection(Connection("Synthetic fixture", "Synthetic model;Roles=admin", 30));
        var builder = new DbConnectionStringBuilder { ConnectionString = test.ConnectionString };
        if (builder.ContainsKey("Roles") || (string)builder["Initial Catalog"] != "Synthetic model;Roles=admin")
            throw new InvalidOperationException();
        Console.WriteLine(JsonSerializer.Serialize(new { status = "PASS", client = typeof(AdomdConnection).Assembly.GetName().Version!.ToString(), runtime = Environment.Version.ToString() }));
        return 0;
    }
    if (args.Length != 0) throw new InvalidOperationException();
    using var input = JsonDocument.Parse(Console.In.ReadToEnd());
    var r = input.RootElement;
    var query = r.GetProperty("query").GetString()!;
    var timeout = r.GetProperty("timeout_seconds").GetInt32();
    // No XMLA control command or executable script is exposed by this helper.
    if (timeout < 1 || timeout > 90 || query.Length > 32000 ||
        !query.TrimStart().StartsWith("EVALUATE", StringComparison.OrdinalIgnoreCase))
        throw new InvalidOperationException();
    var token = r.GetProperty("access_token").GetString()!;
    var part = token.Split('.')[1].Replace('-', '+').Replace('_', '/');
    part = part.PadRight(part.Length + (4 - part.Length % 4) % 4, '=');
    using var claims = JsonDocument.Parse(Convert.FromBase64String(part));
    var expires = DateTimeOffset.FromUnixTimeSeconds(claims.RootElement.GetProperty("exp").GetInt64());
    using var connection = new AdomdConnection(Connection(r.GetProperty("workspace").GetString()!, r.GetProperty("model").GetString()!, timeout));
    connection.AccessToken = new AccessToken(token, expires, null);
    connection.Open();
    using var command = connection.CreateCommand();
    command.CommandTimeout = timeout;
    command.CommandText = query;
    using var reader = command.ExecuteReader();
    var rows = new List<Dictionary<string, object?>>();
    while (reader.Read())
    {
        if (rows.Count >= 10000) throw new InvalidOperationException();
        var row = new Dictionary<string, object?>();
        for (int i = 0; i < reader.FieldCount; i++)
            row.Add(reader.GetName(i), reader.IsDBNull(i) ? null : reader.GetValue(i));
        rows.Add(row);
    }
    if (reader.NextResult()) throw new InvalidOperationException();
    var result = JsonSerializer.Serialize(new { results = new[] { new { tables = new[] { new { rows } } } } });
    if (Encoding.UTF8.GetByteCount(result) > 2097152) throw new InvalidOperationException();
    Console.WriteLine(result);
    return 0;
}
catch
{
    // Native messages can contain tokens or connection details. Never emit them.
    Console.WriteLine("{\"error\":\"XMLA_NATIVE_QUERY_FAILED\"}");
    return 1;
}
