// Explicit portal authoring input; not a published destination declaration.
section Section1;
shared BillingServer = "${BILLING_SQL_SERVER}";
shared BillingDatabase = "billingapp";
shared Accounts = let Source = Sql.Database(BillingServer, BillingDatabase) in Source{[Schema="app", Item="accounts"]}[Data];
shared Plans = let Source = Sql.Database(BillingServer, BillingDatabase) in Source{[Schema="app", Item="plans"]}[Data];
shared AccountPlanHistory = let Source = Sql.Database(BillingServer, BillingDatabase) in Source{[Schema="app", Item="account_plan_history"]}[Data];
shared Invoices = let Source = Sql.Database(BillingServer, BillingDatabase) in Source{[Schema="app", Item="invoices"]}[Data];
shared Payments = let Source = Sql.Database(BillingServer, BillingDatabase) in Source{[Schema="app", Item="payments"]}[Data];
shared UsageEvents = let Source = Sql.Database(BillingServer, BillingDatabase) in Source{[Schema="app", Item="usage_events"]}[Data];
shared Subscriptions = let Source = Sql.Database(BillingServer, BillingDatabase) in Source{[Schema="app", Item="subscriptions"]}[Data];
