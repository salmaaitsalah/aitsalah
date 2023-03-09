#ifndef MY_NEIGHBORLIST_H
#define MY_NEIGHBORLIST_H

#include "ns3/command-line.h"
#include "ns3/nstime.h"
#include "ns3/simulator.h"
#include "ns3/net-device-container.h"
#include "ns3/wave-net-device.h"

using namespace ns3;
typedef struct Neighbor
{
  Address nodeid;
  Time rxtime;
} neighbor;

bool QueueingTimeExceed (neighbor &id);

class NeighborList
{
public:
  void RefreshList (void);
  void UpdateList (const Address &id, Time rx);
  void SetMaxQueueTime (Time duetime);
  uint32_t GetSize (void);

  std::list<neighbor> m_list;
  Time m_maxQueueTime = Seconds (10.0);
};

bool
QueueingTimeExceed (neighbor &node)
{
  // std::cout<< "QueuingTimeEcceed rxtime ="<< node.rxtime <<" time Now "<< Simulator::Now() << " return "<< (Simulator::Now() - (node.rxtime) > Seconds(0))<<std::endl;
  return (Simulator::Now () - (node.rxtime) > Seconds (0));
};

void
NeighborList::RefreshList (void)
{

  m_list.remove_if (QueueingTimeExceed);
};

void
NeighborList::UpdateList (const Address &id, Time rx)
{
  // std::cout<< "rx packet from node "<< id << " at "<< rx << std::endl;
  RefreshList ();
  neighbor node = {id, rx + m_maxQueueTime};
  for (std::list<neighbor>::const_iterator i = m_list.begin (); i != m_list.end (); i++)
    {
      if (i->nodeid == id)
        {
          m_list.erase (i);
          break;
        }
    }
  // std::cout<< "Neighbor list size at node = "<< m_list.size()<< std::endl;
  m_list.push_back (node);
  //  std::cout<< "Neighbor list size at node = "<< m_list.size()<< std::endl;
};

void
NeighborList::SetMaxQueueTime (Time duetime)
{
  m_maxQueueTime = duetime;
};
uint32_t
NeighborList::GetSize (void)
{
  return m_list.size ();
};

#endif // MY_NEIGHBORLIST_H