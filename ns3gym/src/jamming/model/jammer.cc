#include "jammer.h"
#include "ns3/simulator.h"
#include "ns3/log.h"

NS_LOG_COMPONENT_DEFINE ("Jammer");

/*
 * Jammer base class.
 */
namespace ns3 {

NS_OBJECT_ENSURE_REGISTERED (Jammer);

TypeId
Jammer::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::Jammer")
    .SetParent<Object> ()
    ;
  return tid;
}

Jammer::Jammer (void)
  :  m_jammerOn (true) // jammer off by default
{
}

Jammer::~Jammer (void)
{
}

void
Jammer::SetId (uint32_t id)
{
  NS_LOG_FUNCTION (this << id);
  m_id = id;
}

uint32_t
Jammer::GetId (void) const
{
  NS_LOG_FUNCTION (this);
  return m_id;
}

void
Jammer::StartJammer (void)
{
  NS_LOG_FUNCTION (this);
  m_jammerOn = true;  // turn jammer on
  DoJamming ();       // call jamming function
}

void
Jammer::StopJammer (void)
{
  NS_LOG_FUNCTION (this);
  m_jammerOn = false; // turn jammer off
  DoStopJammer ();    // stop jammer
}

bool
Jammer::StartRxHandler (Ptr<WifiPpdu> packet, double startRss)
{
  NS_LOG_FUNCTION (this << packet << startRss);
  if (m_jammerOn)
    {
      return DoStartRxHandler (packet, startRss);
    }
  else
    {
      NS_LOG_DEBUG ("At Node #" << m_id << ", Jammer is OFF, ignoring StartRx!");
      return false; // when jammer is off, all incoming packets are ignored.
    }
}


/*
 * Protected functions start here.
 */

bool
Jammer::IsJammerOn (void) const
{
  return m_jammerOn;
}

} // namespace ns3
