
DROP DATABASE IF EXISTS SecurityOpsCenter;

-- Step 1 — Create the Database
CREATE DATABASE SecurityOpsCenter;

USE SecurityOpsCenter;

-- Step 2 — Create Core Tables with Constraints
CREATE TABLE Employees (
    EmployeeID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    ManagerID INT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Department VARCHAR(50),
    HireDate DATE NOT NULL,
    CONSTRAINT fk_employees_manager FOREIGN KEY (ManagerID) REFERENCES Employees (EmployeeID)
);

CREATE TABLE Assets (
    AssetID INT AUTO_INCREMENT PRIMARY KEY,
    Hostname VARCHAR(100) NOT NULL UNIQUE,
    IPAddress VARCHAR(45) NOT NULL,
    OwnerID INT,
    Criticality VARCHAR(10) CHECK (
        Criticality IN (
            'Low',
            'Medium',
            'High',
            'Critical'
        )
    ),
    FOREIGN KEY (OwnerID) REFERENCES Employees (EmployeeID)
);

CREATE TABLE Vulnerabilities (
    VulnID INT AUTO_INCREMENT PRIMARY KEY,
    CVE_ID VARCHAR(20) UNIQUE,
    Description TEXT,
    Severity VARCHAR(10) CHECK (
        Severity IN (
            'Low',
            'Medium',
            'High',
            'Critical'
        )
    ),
    DiscoveredAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Incidents (
    IncidentID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(150) NOT NULL,
    Status VARCHAR(20) DEFAULT 'Open' CHECK (
        Status IN (
            'Open',
            'Investigating',
            'Resolved',
            'Closed'
        )
    ),
    Severity VARCHAR(10) CHECK (
        Severity IN (
            'Low',
            'Medium',
            'High',
            'Critical'
        )
    ),
    DetectedAt DATETIME NOT NULL,
    ResolvedAt DATETIME
);

CREATE TABLE IncidentAssets (
    IncidentID INT,
    AssetID INT,
    PRIMARY KEY (IncidentID, AssetID),
    FOREIGN KEY (IncidentID) REFERENCES Incidents (IncidentID),
    FOREIGN KEY (AssetID) REFERENCES Assets (AssetID)
);

CREATE TABLE IncidentVulnerabilities (
    IncidentID INT,
    VulnID INT,
    PRIMARY KEY (IncidentID, VulnID),
    FOREIGN KEY (IncidentID) REFERENCES Incidents (IncidentID),
    FOREIGN KEY (VulnID) REFERENCES Vulnerabilities (VulnID)
);

CREATE TABLE AccessLogs (
    LogID INT AUTO_INCREMENT,
    EmployeeID INT,
    AssetID INT,
    Action VARCHAR(50),
    Timestamp DATETIME NOT NULL,
    Success BOOLEAN NOT NULL,
    CONSTRAINT pk_AccessLogs PRIMARY KEY (LogID, Timestamp)
);

--  Step 3 — Insert Sample Data
INSERT INTO
    Employees (
        FirstName,
        LastName,
        ManagerID,
        Email,
        Department,
        HireDate
    )
VALUES (
        'Priya',
        'Nair',
        NULL,
        'priya.nair@corp.com',
        'SecOps',
        '2022-01-10'
    ),
    (
        'Maria',
        'Lopez',
        1,
        'maria.lopez@corp.com',
        'IT',
        '2021-03-01'
    ),
    (
        'Sam',
        'Chen',
        1,
        'sam.chen@corp.com',
        'Finance',
        '2020-07-15'
    ),
    (
        'Tom',
        'Reed',
        2,
        'tom.reed@corp.com',
        'HR',
        '2019-11-20'
    );

INSERT INTO
    Assets (
        Hostname,
        IPAddress,
        OwnerID,
        Criticality
    )
VALUES (
        'FIN-SRV-01',
        '10.0.1.15',
        2,
        'Critical'
    ),
    (
        'IT-WKS-04',
        '10.0.2.44',
        1,
        'Medium'
    ),
    (
        'HR-WKS-11',
        '10.0.3.22',
        4,
        'Low'
    ),
    (
        'SEC-SRV-02',
        '10.0.1.50',
        3,
        'Critical'
    );

INSERT INTO
    Vulnerabilities (CVE_ID, Description, Severity)
VALUES (
        'CVE-2024-1234',
        'Remote code execution in outdated web server',
        'Critical'
    ),
    (
        'CVE-2023-5678',
        'Privilege escalation via misconfigured service',
        'High'
    ),
    (
        'CVE-2024-0099',
        'Weak TLS configuration',
        'Medium'
    );

INSERT INTO
    Incidents (
        Title,
        Status,
        Severity,
        DetectedAt
    )
VALUES (
        'Unusual outbound traffic from FIN-SRV-01',
        'Investigating',
        'Critical',
        '2026-06-01 03:14:00'
    ),
    (
        'Multiple failed logins on SEC-SRV-02',
        'Open',
        'High',
        '2026-06-03 22:40:00'
    ),
    (
        'Outdated TLS flagged by scanner',
        'Resolved',
        'Medium',
        '2026-05-20 09:00:00'
    );

INSERT INTO IncidentAssets VALUES (1, 1), (2, 4), (3, 4);

INSERT INTO IncidentVulnerabilities VALUES (1, 1), (3, 3);

INSERT INTO
    AccessLogs (
        EmployeeID,
        AssetID,
        Action,
        Timestamp,
        Success
    )
VALUES (
        2,
        1,
        'LOGIN',
        '2026-06-01 03:10:00',
        FALSE
    ),
    (
        2,
        1,
        'LOGIN',
        '2026-06-01 03:11:00',
        FALSE
    ),
    (
        2,
        1,
        'LOGIN',
        '2026-06-01 03:12:00',
        FALSE
    ),
    (
        2,
        1,
        'LOGIN',
        '2026-06-01 03:13:00',
        FALSE
    ),
    (
        2,
        1,
        'LOGIN',
        '2026-06-01 03:14:00',
        TRUE
    ),
    (
        3,
        4,
        'LOGIN',
        '2026-06-03 22:38:00',
        FALSE
    ),
    (
        3,
        4,
        'LOGIN',
        '2026-06-03 22:39:00',
        FALSE
    );

-- Step 4 — Basic Filtering (WHERE, AND/OR/NOT, BETWEEN, LIKE, IN)
-- Failed login attempts only
SELECT * FROM AccessLogs WHERE Success = FALSE;

-- Critical or High severity incidents
SELECT * FROM Incidents WHERE Severity IN ('Critical', 'High');

-- Incidents detected in a specific window (a common SOC query)
SELECT *
FROM Incidents
WHERE
    DetectedAt BETWEEN '2026-06-01' AND '2026-06-30';

-- Hostnames belonging to a subnet
SELECT * FROM Assets WHERE IPAddress LIKE '10.0.1.%';

-- Employees NOT in Finance
SELECT * FROM Employees WHERE NOT Department = 'Finance';

-- Step 5 — Brute-Force Detection (the centerpiece query)
SELECT
    EmployeeID,
    AssetID,
    COUNT(*) AS FailedAttempts
FROM AccessLogs
WHERE
    Success = FALSE
    AND Timestamp > '2026-06-01 00:00:00'
GROUP BY
    EmployeeID,
    AssetID
HAVING
    COUNT(*) >= 3;

-- Step 6 — JOINs (all four types, with a security narrative)
-- INNER JOIN: incidents with their affected assets
SELECT i.Title, a.Hostname, a.Criticality
FROM
    Incidents i
    INNER JOIN IncidentAssets ia ON i.IncidentID = ia.IncidentID
    INNER JOIN Assets a ON ia.AssetID = a.AssetID;

-- LEFT JOIN: every asset, even ones with zero incidents (helps show "healthy" systems too)
SELECT a.Hostname, i.Title
FROM
    Assets a
    LEFT JOIN IncidentAssets ia ON a.AssetID = ia.AssetID
    LEFT JOIN Incidents i ON ia.IncidentID = i.IncidentID;

-- RIGHT JOIN: every incident, even ones not yet linked to an asset
SELECT a.Hostname, i.Title
FROM
    Assets a
    RIGHT JOIN IncidentAssets ia ON a.AssetID = ia.AssetID
    RIGHT JOIN Incidents i ON ia.IncidentID = i.IncidentID;

-- Simulated FULL JOIN (MySQL has no native FULL JOIN)
SELECT a.Hostname, i.Title
FROM
    Assets a
    LEFT JOIN IncidentAssets ia ON a.AssetID = ia.AssetID
    LEFT JOIN Incidents i ON ia.IncidentID = i.IncidentID
UNION
SELECT a.Hostname, i.Title
FROM
    Assets a
    RIGHT JOIN IncidentAssets ia ON a.AssetID = ia.AssetID
    RIGHT JOIN Incidents i ON ia.IncidentID = i.IncidentID;

-- Step 7 — Window Functions (the differentiator most freshers skip)
-- Rank employees by failed login count (RANK / DENSE_RANK)
SELECT
    EmployeeID,
    COUNT(*) AS FailedAttempts,
    RANK() OVER (
        ORDER BY COUNT(*) DESC
    ) AS RiskRank
FROM AccessLogs
WHERE
    Success = FALSE
GROUP BY
    EmployeeID;

-- Rolling count: failed attempts in the preceding 3 events per employee (LAG example)
SELECT
    EmployeeID,
    Timestamp,
    Success,
    LAG(Timestamp) OVER (
        PARTITION BY
            EmployeeID
        ORDER BY Timestamp
    ) AS PrevAttemptTime,
    TIMESTAMPDIFF(
        SECOND,
        LAG(Timestamp) OVER (
            PARTITION BY
                EmployeeID
            ORDER BY Timestamp
        ),
        Timestamp
    ) AS SecondsSinceLastAttempt
FROM AccessLogs
ORDER BY EmployeeID, Timestamp;

-- Step 8 — CTEs and Recursive Queries (attacker path tracing)
-- Simple CTE: isolate high-risk assets first, then join
WITH
    HighRiskAssets AS (
        SELECT AssetID, Hostname
        FROM Assets
        WHERE
            Criticality = 'Critical'
    )
SELECT h.Hostname, i.Title, i.Severity
FROM
    HighRiskAssets h
    JOIN IncidentAssets ia ON h.AssetID = ia.AssetID
    JOIN Incidents i ON ia.IncidentID = i.IncidentID;

-- Recursive CTE example: organizational reporting chain (useful if you add a ManagerID column)
-- ALTER TABLE Employees ADD ManagerID INT NULL;
WITH RECURSIVE
    ReportingChain AS (
        SELECT
            EmployeeID,
            FirstName,
            ManagerID,
            1 AS Level
        FROM Employees
        WHERE
            ManagerID IS NULL
        UNION ALL
        SELECT e.EmployeeID, e.FirstName, e.ManagerID, rc.Level + 1
        FROM
            Employees e
            JOIN ReportingChain rc ON e.ManagerID = rc.EmployeeID
    )
SELECT *
FROM ReportingChain;

--  Step 9 — Indexing and Query Optimization
-- Composite index on the columns your brute-force query filters/groups by
CREATE INDEX idx_accesslogs_time_emp ON AccessLogs (
    Timestamp,
    EmployeeID,
    Success
);

-- Verify it's used
EXPLAIN
SELECT EmployeeID, COUNT(*)
FROM AccessLogs
WHERE
    Success = FALSE
    AND Timestamp > '2026-06-01'
GROUP BY
    EmployeeID;

SHOW INDEXES FROM AccessLogs;

-- Step 10 — Views
CREATE VIEW SuspiciousActivity AS
SELECT
    al.EmployeeID,
    e.FirstName,
    e.LastName,
    al.AssetID,
    a.Hostname,
    COUNT(*) AS FailedAttempts,
    MAX(al.Timestamp) AS LastAttempt
FROM
    AccessLogs al
    JOIN Employees e ON al.EmployeeID = e.EmployeeID
    JOIN Assets a ON al.AssetID = a.AssetID
WHERE
    al.Success = FALSE
GROUP BY
    al.EmployeeID,
    al.AssetID
HAVING
    COUNT(*) >= 3;

SELECT * FROM SuspiciousActivity;

-- Step 11 — Triggers (auto-flagging compromised assets)

CREATE TRIGGER trg_flag_critical_incident
AFTER INSERT ON IncidentVulnerabilities
FOR EACH ROW
BEGIN
    DECLARE vSeverity VARCHAR(10);
    SELECT Severity INTO vSeverity FROM Vulnerabilities WHERE VulnID = NEW.VulnID;
    IF vSeverity = 'Critical' THEN
        UPDATE Incidents SET Severity = 'Critical' WHERE IncidentID = NEW.IncidentID;
    END IF;
END 


-- Step 12 — Transactions (atomic incident resolution)
START TRANSACTION;

UPDATE Incidents
SET
    Status = 'Resolved',
    ResolvedAt = NOW()
WHERE
    IncidentID = 3;

INSERT INTO
    AccessLogs (
        EmployeeID,
        AssetID,
        Action,
        Timestamp,
        Success
    )
VALUES (
        3,
        4,
        'INCIDENT_CLOSED',
        NOW(),
        TRUE
    );

COMMIT;
-- ROLLBACK; would undo both statements if something failed

--  Step 13 — Stored Procedures

CREATE PROCEDURE GetIncidentsByAsset(IN inAssetID INT)
BEGIN
    SELECT i.* FROM Incidents i
    JOIN IncidentAssets ia ON i.IncidentID = ia.IncidentID
    WHERE ia.AssetID = inAssetID;
END 

CREATE PROCEDURE LockAccountAfterNFailures(IN inEmployeeID INT, IN threshold INT)
BEGIN
    DECLARE failCount INT;
    SELECT COUNT(*) INTO failCount
    FROM AccessLogs
    WHERE EmployeeID = inEmployeeID AND Success = FALSE
      AND Timestamp > NOW() - INTERVAL 1 HOUR;

    IF failCount >= threshold THEN
        SELECT CONCAT('ALERT: Employee ', inEmployeeID, ' exceeded ', threshold, ' failed attempts.') AS Result;
    ELSE
        SELECT 'OK' AS Result;
    END IF;
END 

CALL GetIncidentsByAsset (1);

CALL LockAccountAfterNFailures (2, 3);

-- Step 14 — Role-Based Access Control (the security-specific piece that stands out most)
CREATE USER 'soc_analyst' @'localhost' IDENTIFIED BY 'AnalystPass123!';

CREATE USER 'soc_admin' @'localhost' IDENTIFIED BY 'AdminPass123!';

-- Analyst: read-only on incident data, no access to raw employee PII
GRANT
SELECT ON SecurityOpsCenter.Incidents TO 'soc_analyst' @'localhost';

GRANT
SELECT ON SecurityOpsCenter.SuspiciousActivity TO 'soc_analyst' @'localhost';

-- Admin: full control
GRANT ALL PRIVILEGES ON SecurityOpsCenter.* TO 'soc_admin' @'localhost';

SHOW GRANTS FOR 'soc_analyst' @'localhost';

-- Revoke as needed
REVOKE ALL PRIVILEGES ON SecurityOpsCenter.*
FROM 'soc_admin' @'localhost';

-- Step 15 — Full-Text Search (searching incident narratives)
ALTER TABLE Incidents ADD FULLTEXT (Title);

SELECT *
FROM Incidents
WHERE
    MATCH(Title) AGAINST (
        'failed logins outbound traffic' IN NATURAL LANGUAGE MODE
    );

-- Step 16 — Partitioning Large Log Tables (for scale talking points)
-- If AccessLogs grows into millions of rows, partition by month for faster pruning
ALTER TABLE AccessLogs
PARTITION BY
    RANGE (
        YEAR(Timestamp) * 100 + MONTH(Timestamp)
    ) (
        PARTITION p202605
        VALUES
            LESS THAN (202606),
            PARTITION p202606
        VALUES
            LESS THAN (202607),
            PARTITION pMax
        VALUES
            LESS THAN MAXVALUE
    );

