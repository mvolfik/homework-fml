# Homework – Fully Merged List

*Import your tasks from various systems (Moodle, Google Classroom, Bakaláři, or note
them yourself) and manage them in one simple list.*

A second _"iteration"_ of [Bakatasklist](https://github.com/mvolfik/Bakalari-homework-tasklist)

---

Todo list, don't forget me notes, etc.:

- Fixme: There are multiple issues around login/pwd verification, verification
email resending and password reset:
  - Login currently checks password first, and only after correct password it offers
  re-sending the verification email.
  - However, the API doesn't restrict email resend in any way, so it's easy to spam user
  with verification emails.
  - It's also very easy to detect if an email is registered via the reset password API.
  It doesn't tell you, but it takes significantly longer for registered users, as it has
  to send the email before returning. --> we'll need workers for import anyways, so
  include the mailing there too

- Feature: periodic automatic import, send email to user when new homework appears.
Possibly premium feature

- Feature: homework "shared lists" - you create a list that your classmates can
subscribe to (and optionally contribute? - generate two urls, one for write, one for
read-only)

- Fixme: require action on verify email page (some services preload links in e-mails)