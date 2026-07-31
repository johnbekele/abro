# ADR 0008 — Telegram-first OTP, SMS as fallback

**Status:** accepted · **Date:** 2026-07-31

## Context

Phone number is the identity in abro, so OTP delivery is on the critical path for every signup and
every login. Ethiopia is an unusual market for this.

## Decision

A cascade, tried in order, behind a single channel interface:

1. **Telegram Gateway.** `checkSendAbility` first — it is free and tells us whether the number can
   receive a Telegram message at all. If yes, send: **$0.01**, refunded automatically if
   undelivered.
2. **Local SMS aggregator** (AfroMessage or SMSEthiopia), roughly $0.001–0.003 per message with a
   direct Ethio Telecom connection.
3. **Voice call**, last resort.

`mock` is the default in development and CI, printing the code to the log.

## Why Telegram first

Ethiopia is a genuine global outlier. A 27-country African study found WhatsApp was the preferred
messaging app in 25 of them — the exceptions being Algeria and **Ethiopia, where Telegram wins**.
Surveys put Telegram usage at 96–98% among Ethiopian university students. Even Fayda, the national
ID programme, runs its developer support on Telegram.

The cost gap is decisive: **$0.01 via Telegram against $0.3425 for Twilio SMS to +251**, a factor
of 34. And the free reachability pre-check means unreachable numbers cost nothing before falling
through.

Telegram is also a better *notification* channel than email here — trip reminders, driver contact,
a pickup pin — because it is low-data, familiar, and survives when push does not.

## Why not the alternatives

- **Twilio and other international aggregators** are viable technically and impossible
  economically at consumer scale against Ethiopian ARPUs.
- **WhatsApp Business API** works in Ethiopia but reaches far fewer people than Telegram, and the
  authentication-international rate applies if the business account is registered outside
  Ethiopia — which can be an order of magnitude more expensive.
- **Flash call / missed-call verification** is cheap but fails silently on poor voice
  infrastructure and on dual-SIM devices, which are the norm on Transsion handsets here.
- **Silent network authentication** covers about fifteen countries. Ethiopia is not one.

## Consequences

- **Ethio Telecom blocks unregistered alphanumeric sender IDs from 8 October 2026.** Registration
  takes one to two weeks and needs company details and a VAT number. Launch-blocking.
- Production SMS credentials require a registered Ethiopian business with a current trade licence.
  Development does not, because of the `mock` channel.
- Keep an international provider configured as a last-resort failover, **rate-limited**, so a
  misconfiguration cannot produce a five-figure bill.
- Use a 6-digit code. BlaBlaCar's 4-digit code is below current practice.
- Push notifications are best-effort and never the only channel for anything that matters:
  Transsion devices dominate Ethiopia and kill background apps aggressively. Booking confirmed,
  driver cancelled and driver arriving all go out over Telegram or SMS as well.
