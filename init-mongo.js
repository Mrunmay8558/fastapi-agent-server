// MongoDB initialization script
db = db.getSiblingDB("agent_server_db");

// Create indexes for better performance
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ username: 1 }, { unique: true });
db.users.createIndex({ is_active: 1 });
db.users.createIndex({ created_at: 1 });

db.agents.createIndex({ created_by: 1 });
db.agents.createIndex({ is_active: 1 });
db.agents.createIndex({ name: "text", description: "text" });
db.agents.createIndex({ created_at: 1 });

print("Database initialized with indexes");
