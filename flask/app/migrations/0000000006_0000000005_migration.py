revision = "0000000006"
down_revision = "0000000005"


def upgrade(migration):
    # Create the "todo" table
    migration.create_table(
        "todo",
        """
            "entity_id" varchar(32) NOT NULL,
            "version" varchar(32) NOT NULL,
            "previous_version" varchar(32) DEFAULT '00000000000000000000000000000000',
            "active" boolean DEFAULT true,
            "changed_on" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
            "title" varchar(255) NOT NULL,
            "description" text,
            "changed_by_id" varchar(32) DEFAULT NULL,
            "is_completed" boolean DEFAULT false,
            "completed_at" timestamp NULL,
            "due_date" timestamp NULL,
            "priority" integer DEFAULT 0,
            "person_id" varchar(32) NOT NULL,
            PRIMARY KEY ("entity_id"),
            CONSTRAINT "fk_todo_person" FOREIGN KEY ("person_id") 
                REFERENCES "person" ("entity_id") ON DELETE CASCADE
        """
    )
    
    # Add indexes for better query performance
    migration.add_index("todo", "todo_person_id_ind", "person_id")
    migration.add_index("todo", "todo_is_completed_ind", "is_completed")
    migration.add_index("todo", "todo_person_completed_ind", "person_id, is_completed, active")

    # Create the audit table for todo
    migration.create_table(
        "todo_audit",
        """
            "entity_id" varchar(32) NOT NULL,
            "version" varchar(32) NOT NULL,
            "previous_version" varchar(32) DEFAULT '00000000000000000000000000000000',
            "active" boolean DEFAULT true,
            "changed_on" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
            "title" varchar(255) NOT NULL,
            "description" text,
            "changed_by_id" varchar(32) DEFAULT NULL,
            "is_completed" boolean DEFAULT false,
            "completed_at" timestamp NULL,
            "due_date" timestamp NULL,
            "priority" integer DEFAULT 0,
            "person_id" varchar(32) NOT NULL,
            PRIMARY KEY ("entity_id", "version")
        """
    )

    migration.update_version_table(version=revision)


def downgrade(migration):
    # Drop the tables in reverse order
    migration.drop_table(table_name="todo_audit")
    migration.drop_table(table_name="todo")

    migration.update_version_table(version=down_revision) 
