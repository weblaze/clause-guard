// Jurisdictions with real, researched statute coverage in the backend knowledge base.
// Mirrors backend/knowledge_base/jurisdiction_guide.json for the subset of states that
// have deep, cited statute entries (not just a category label) - keeping the dropdown
// scoped to what the RAG pipeline can actually ground an answer in.
export interface JurisdictionInfo {
  value: string;
  label: string;
  actName: string;
  note: string;
}

export const JURISDICTIONS: JurisdictionInfo[] = [
  {
    value: 'Central',
    label: 'India Central (MTA 2021)',
    actName: 'Model Tenancy Act, 2021',
    note: "The Central Model Tenancy Act is a template law for states to adopt - it isn't automatically binding everywhere. Use this when your state has its own Model-Tenancy-style law or no distinct act of its own.",
  },
  {
    value: 'Delhi',
    label: 'Delhi',
    actName: 'Delhi Rent Control Act, 1958',
    note: 'Applies only where monthly rent is Rs. 3,500 or less. Most modern leases exceed this and fall under general contract law instead.',
  },
  {
    value: 'Maharashtra',
    label: 'Maharashtra',
    actName: 'Maharashtra Rent Control Act, 1999',
    note: 'Sets standard rent and restricted eviction grounds; does not fix a statutory security deposit cap.',
  },
  {
    value: 'Uttar Pradesh',
    label: 'Uttar Pradesh',
    actName: 'UP Regulation of Urban Premises Tenancy Act, 2021',
    note: 'Modelled on the Central Model Tenancy Act, with its own Rent Authority/Tribunal system.',
  },
  {
    value: 'Gujarat',
    label: 'Gujarat',
    actName: 'Gujarat Rents, Hotel and Lodging House Rates Control Act, 1947',
    note: 'A repeatedly-extended 1947 law; premises built after 2001 and government-owned premises are excluded.',
  },
  {
    value: 'Rajasthan',
    label: 'Rajasthan',
    actName: 'Rajasthan Rent Control Act, 2001',
    note: 'Disputes go to dedicated Rent Tribunals; security deposit is capped at one month’s rent by default.',
  },
  {
    value: 'Telangana',
    label: 'Telangana',
    actName: 'Telangana Buildings (Lease, Rent and Eviction) Control Act, 1960',
    note: 'Carried over from undivided Andhra Pradesh; advance rent capped at one month.',
  },
  {
    value: 'Kerala',
    label: 'Kerala',
    actName: 'Kerala Buildings (Lease and Rent Control) Act, 1965',
    note: 'Applies only within municipal/corporation limits - panchayat-area lettings fall under general contract law.',
  },
  {
    value: 'Punjab',
    label: 'Punjab',
    actName: 'Punjab Rent Act, 1995',
    note: 'In force since 2013; no statutory deposit cap, but advances must be refunded with interest on delay.',
  },
  {
    value: 'Haryana',
    label: 'Haryana',
    actName: 'Haryana Urban (Control of Rent and Eviction) Act, 1973',
    note: 'Buildings under 10 years old and cantonment areas are exempt from this Act.',
  },
  {
    value: 'Madhya Pradesh',
    label: 'Madhya Pradesh',
    actName: 'Madhya Pradesh Accommodation Control Act, 1961',
    note: 'New construction is exempt for 5 years; advance rent capped at one month absent special permission.',
  },
  {
    value: 'Bihar',
    label: 'Bihar',
    actName: 'Bihar Buildings (Lease, Rent and Eviction) Control Act, 1982',
    note: 'Eviction requires a court decree on specified grounds; premium/advance beyond one month’s rent is barred.',
  },
  {
    value: 'Tamil Nadu',
    label: 'Tamil Nadu',
    actName: 'Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017',
    note: 'Mandatory tenancy registration; security deposit defaults to 3 months’ rent if the agreement is silent.',
  },
  {
    value: 'Karnataka',
    label: 'Karnataka',
    actName: 'Karnataka Rent Act, 1999',
    note: 'No confirmed statutory deposit cap despite widely-circulated claims of a 2025 amendment adding one - verify current market terms independently.',
  },
  {
    value: 'West Bengal',
    label: 'West Bengal',
    actName: 'West Bengal Premises Tenancy Act, 1997',
    note: 'Covers Kolkata, Howrah and other notified areas; advance rent capped at one month, no premium allowed.',
  },
];
