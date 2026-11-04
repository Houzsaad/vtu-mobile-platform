export function normalizePhone(raw) {
  let d = String(raw).replace(/\D/g, '');
  if (d.startsWith('234') && d.length >= 13) d = '0' + d.slice(3, 13);
  if (d.length === 10) d = '0' + d;
  return d.slice(0, 11);
}

export const canPickContact =
  typeof navigator !== 'undefined' && 'contacts' in navigator && 'ContactsManager' in window;

export async function pickContactNumber() {
  try {
    const [contact] = await navigator.contacts.select(['tel'], { multiple: false });
    return contact?.tel?.length ? normalizePhone(contact.tel[0]) : '';
  } catch {
    return ''; // cancelled or refused: the user can still type the number
  }
}