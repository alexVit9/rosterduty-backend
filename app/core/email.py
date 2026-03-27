from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME="RosterDuty",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fm = FastMail(mail_config)

APP_URL = "https://rosterduty.com"


def _build_invite_html(
    recipient_name: str,
    restaurant_name: str,
    invite_token: str,
    invite_link: str,
) -> str:
    digits = list(invite_token.zfill(4))
    return f"""<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <title>You're invited to RosterDuty</title>
  <!--[if mso]>
  <noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript>
  <![endif]-->
</head>
<body style="margin:0;padding:0;background-color:#f4f4f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">

  <!-- Preheader -->
  <div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">
    You've been invited to join {restaurant_name} on RosterDuty &#8203;&zwnj;&nbsp;&#847;&#zwnj;&#8203;&nbsp;&#847;&#zwnj;&#8203;&nbsp;&#847;
  </div>

  <!-- Wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f4f4f5;">
    <tr>
      <td align="center" style="padding:24px 16px;">

        <!-- Card -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:560px;background-color:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">

          <!-- ── HEADER ── -->
          <tr>
            <td style="background:linear-gradient(135deg,#ea580c 0%,#f97316 100%);padding:16px 28px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td>
                    <table cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td style="background-color:rgba(255,255,255,0.2);border-radius:8px;padding:5px 8px;vertical-align:middle;">
                          <span style="font-size:14px;font-weight:800;color:#ffffff;">✓</span>
                        </td>
                        <td style="padding-left:8px;vertical-align:middle;">
                          <span style="font-size:17px;font-weight:800;color:#ffffff;letter-spacing:-0.3px;">RosterDuty</span>
                        </td>
                      </tr>
                    </table>
                  </td>
                  <td align="right" style="vertical-align:middle;">
                    <span style="display:inline-block;background-color:rgba(255,255,255,0.2);border-radius:20px;padding:3px 10px;font-size:10px;font-weight:600;color:#ffffff;letter-spacing:0.5px;text-transform:uppercase;">Team Invitation</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ── HERO ── -->
          <tr>
            <td style="padding:24px 28px 16px;">
              <p style="margin:0 0 4px;font-size:13px;color:#9ca3af;font-weight:500;">Hi {recipient_name},</p>
              <h1 style="margin:0 0 8px;font-size:22px;font-weight:800;color:#111827;line-height:1.25;letter-spacing:-0.3px;">
                You've been invited to join <span style="color:#f97316;">{restaurant_name}</span>
              </h1>
              <p style="margin:0;font-size:14px;color:#6b7280;line-height:1.5;">
                Your team uses RosterDuty to manage tasks and checklists. Accept your invitation to get started.
              </p>
            </td>
          </tr>

          <!-- ── PRIMARY CTA ── -->
          <tr>
            <td style="padding:12px 28px 16px;">
              <table cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="border-radius:10px;background:linear-gradient(135deg,#ea580c 0%,#f97316 100%);">
                    <a href="{APP_URL}" target="_blank"
                       style="display:inline-block;padding:11px 26px;font-size:14px;font-weight:700;color:#ffffff;text-decoration:none;border-radius:10px;">
                      Open RosterDuty &rarr;
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ── DIVIDER ── -->
          <tr>
            <td style="padding:0 28px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr><td style="border-top:1px solid #f3f4f6;"></td></tr>
              </table>
            </td>
          </tr>

          <!-- ── INVITE CODE BLOCK ── -->
          <tr>
            <td style="padding:16px 28px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                     style="background-color:#fff7ed;border-radius:10px;border:1.5px solid #fed7aa;">
                <tr>
                  <td style="padding:16px 20px;" align="center">
                    <p style="margin:0 0 10px;font-size:11px;font-weight:700;color:#9a3412;letter-spacing:1px;text-transform:uppercase;">Your 4-digit invite code</p>
                    <table cellpadding="0" cellspacing="0" border="0" style="margin:0 auto;">
                      <tr>
                        <td style="padding:0 4px;">
                          <div style="width:48px;height:58px;background-color:#ffffff;border-radius:10px;border:2px solid #f97316;display:inline-block;text-align:center;line-height:58px;font-size:30px;font-weight:800;color:#111827;">{digits[0]}</div>
                        </td>
                        <td style="padding:0 4px;">
                          <div style="width:48px;height:58px;background-color:#ffffff;border-radius:10px;border:2px solid #f97316;display:inline-block;text-align:center;line-height:58px;font-size:30px;font-weight:800;color:#111827;">{digits[1]}</div>
                        </td>
                        <td style="padding:0 4px;">
                          <div style="width:48px;height:58px;background-color:#ffffff;border-radius:10px;border:2px solid #f97316;display:inline-block;text-align:center;line-height:58px;font-size:30px;font-weight:800;color:#111827;">{digits[2]}</div>
                        </td>
                        <td style="padding:0 4px;">
                          <div style="width:48px;height:58px;background-color:#ffffff;border-radius:10px;border:2px solid #f97316;display:inline-block;text-align:center;line-height:58px;font-size:30px;font-weight:800;color:#111827;">{digits[3]}</div>
                        </td>
                      </tr>
                    </table>
                    <p style="margin:10px 0 0;font-size:12px;color:#92400e;">
                      Enter this code in the app after opening your invitation
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ── ALTERNATIVE LINK ── -->
          <tr>
            <td style="padding:0 28px 16px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                     style="background-color:#f9fafb;border-radius:10px;border:1px solid #e5e7eb;">
                <tr>
                  <td style="padding:14px 18px;">
                    <p style="margin:0 0 8px;font-size:12px;color:#6b7280;">
                      Or accept your invitation using your personal link:
                    </p>
                    <table cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td style="border-radius:7px;border:1.5px solid #e5e7eb;background-color:#ffffff;">
                          <a href="{invite_link}" target="_blank"
                             style="display:inline-block;padding:8px 16px;font-size:13px;font-weight:600;color:#374151;text-decoration:none;border-radius:7px;">
                            Accept Invitation &rarr;
                          </a>
                        </td>
                      </tr>
                    </table>
                    <p style="margin:6px 0 0;font-size:10px;color:#d1d5db;word-break:break-all;">{invite_link}</p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ── EXPIRY ── -->
          <tr>
            <td style="padding:0 28px 20px;">
              <p style="margin:0;font-size:12px;color:#9ca3af;border-left:3px solid #fed7aa;padding-left:10px;line-height:1.5;">
                <strong style="color:#374151;">Expires in 7 days.</strong>
                If you weren't expecting this, you can safely ignore it.
              </p>
            </td>
          </tr>

          <!-- ── FOOTER ── -->
          <tr>
            <td style="background-color:#f9fafb;border-top:1px solid #f3f4f6;padding:14px 28px;" align="center">
              <p style="margin:0;font-size:12px;color:#9ca3af;">
                <strong style="color:#374151;">RosterDuty</strong> — Restaurant Operations, Simplified
              </p>
            </td>
          </tr>

        </table>
        <!-- /Card -->

      </td>
    </tr>
  </table>

</body>
</html>"""


def _build_invite_plain(
    recipient_name: str,
    restaurant_name: str,
    invite_token: str,
    invite_link: str,
) -> str:
    return f"""Hi {recipient_name},

You've been invited to join {restaurant_name} on RosterDuty.

Your team uses RosterDuty to manage restaurant operations, tasks, and checklists in one place.

──────────────────────────
OPEN THE APP
──────────────────────────
{APP_URL}

──────────────────────────
YOUR 4-DIGIT INVITE CODE
──────────────────────────
  {invite_token}

Enter this code in the app after opening your invitation.

──────────────────────────
OR USE YOUR PERSONAL LINK
──────────────────────────
{invite_link}

This invitation is valid for 7 days.

If you weren't expecting this invitation, you can safely ignore this email.

—
RosterDuty — Restaurant Operations, Simplified"""


async def send_invite_email(
    recipient_email: str,
    recipient_name: str,
    restaurant_name: str,
    invite_token: str,
) -> None:
    invite_link = f"{settings.FRONTEND_URL}/invite/accept?token={invite_token}"

    html_body = _build_invite_html(
        recipient_name=recipient_name,
        restaurant_name=restaurant_name,
        invite_token=invite_token,
        invite_link=invite_link,
    )

    message = MessageSchema(
        subject=f"You're invited to join {restaurant_name} on RosterDuty",
        recipients=[recipient_email],
        body=html_body,
        subtype=MessageType.html,
    )

    await fm.send_message(message)
