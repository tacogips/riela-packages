const greetings = [
  "Hello",
  "Good morning",
  "Good afternoon",
  "Good evening",
  "Welcome back"
];

const name = process.argv[2] && process.argv[2].trim().length > 0
  ? process.argv[2].trim()
  : "friend";
const timezone = process.env.GREETING_TIMEZONE && process.env.GREETING_TIMEZONE.trim().length > 0
  ? process.env.GREETING_TIMEZONE.trim()
  : "UTC";
const rawIndex = Number.parseInt(process.env.GREETING_INDEX ?? "0", 10);
const index = Number.isFinite(rawIndex) ? Math.abs(rawIndex) % greetings.length : 0;
const now = new Date();
const greeting = greetings[index];

const output = {
  runtime: "container-node",
  greeting,
  name,
  message: `${greeting}, ${name}. The current time is ${now.toISOString()}.`,
  datetime: {
    iso: now.toISOString(),
    local: new Intl.DateTimeFormat("en-US", {
      dateStyle: "full",
      timeStyle: "long",
      timeZone: timezone
    }).format(now),
    timezone
  },
  greetingsAvailable: greetings
};

process.stdout.write(`${JSON.stringify(output)}\n`);
