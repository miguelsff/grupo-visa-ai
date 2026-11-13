# NexoOPS color system

Reference: the supplied white and lavender chat interface. Prioritize calm white surfaces, soft gray sidebar, near-black text and restrained lavender highlights.

| Role | Light | Use |
|---|---|---|
| Surface | #FFFFFF | Chat, canvas, input |
| Canvas | #F5F4F6 | Sidebar and outer surfaces |
| Ink | #211F26 | Text and primary actions |
| Secondary | #68616F | Supporting text |
| Accent | #7653A8 | Focus, tabs and progress |
| Accent soft | #E9DFF7 | Avatars and selection |
| Soft | #F2EDF9 | Sources and generated content |
| Border | #E5E1EA | Dividers and fields |
| Success | #257354 | Confirmations |
| Warning | #94620B | Resource conflicts |

Implementation: app/theme.css. All component colors map to semantic variables; dark mode remaps these same roles. Retain Manrope for UI and DM Mono for identifiers. Keep chat text within 780px, aligned left. Color indicates state alongside explicit text.
