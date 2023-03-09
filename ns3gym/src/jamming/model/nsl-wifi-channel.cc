/* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2006,2007 INRIA
 * Copyright (c) 2010 Network Security Lab, University of Washington, Seattle.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Authors: Mathieu Lacage <mathieu.lacage@sophia.inria.fr>
 *          Sidharth Nabar <snabar@uw.edu>, He Wu <mdzz@u.washington.edu>
 */

#include "ns3/packet.h"
#include "ns3/simulator.h"
#include "ns3/mobility-model.h"
#include "ns3/net-device.h"
#include "ns3/node.h"
#include "ns3/log.h"
#include "ns3/pointer.h"
#include "ns3/object-factory.h"
#include "ns3/propagation-loss-model.h"
#include "ns3/propagation-delay-model.h"
#include "nsl-wifi-channel.h"
#include "ns3/wifi-utils.h"
#include "jammer-wifi-phy.h"

NS_LOG_COMPONENT_DEFINE ("NslWifiChannel");

namespace ns3 {

TypeId
NslWifiChannel::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::NslWifiChannel")
    .SetParent<YansWifiChannel> ()
    .AddConstructor<NslWifiChannel> ()
  /*  .AddAttribute ("PropagationLossModel", "A pointer to the propagation loss model attached to this channel.",
                   PointerValue (),
                   MakePointerAccessor (&NslWifiChannel::m_loss),
                   MakePointerChecker<PropagationLossModel> ())
    .AddAttribute ("PropagationDelayModel", "A pointer to the propagation delay model attached to this channel.",
                   PointerValue (),
                   MakePointerAccessor (&NslWifiChannel::m_delay),
                   MakePointerChecker<PropagationDelayModel> ())*/
    ;
  return tid;
}

NslWifiChannel::NslWifiChannel ()
{}
NslWifiChannel::~NslWifiChannel ()
{
  NS_LOG_FUNCTION_NOARGS ();
  YansWifiChannel::GetPhyList().clear ();
}
/*
void
NslWifiChannel::SetPropagationLossModel (Ptr<PropagationLossModel> loss)
{
  m_loss = loss;
}

void
NslWifiChannel::SetPropagationDelayModel (Ptr<PropagationDelayModel> delay)
{
  m_delay = delay;
}

void
NslWifiChannel::Send (Ptr<WifiPhy> sender, Ptr<const WifiPpdu> ppdu, double txPowerDbm)
{
  NS_LOG_FUNCTION (this <<sender << ppdu << txPowerDbm);
 // std::cout<<"NslWifiChannel::Send "<<std::endl;
  Ptr<MobilityModel> senderMobility = sender->GetMobility ();
  NS_ASSERT (senderMobility != 0);
  YansWifiChannel::PhyList phylist = YansWifiChannel::GetPhyList();

  for (PhyList::const_iterator i = phylist.begin (); i != phylist.end (); i++)
    {
      if (sender != (*i))
        {
          // For now don't account for inter channel interference
          if ((*i)->GetChannelNumber() != sender->GetChannelNumber())
              continue;

          Ptr<MobilityModel> receiverMobility = (*i)->GetMobility ()->GetObject<MobilityModel> ();
          Time delay = m_delay->GetDelay (senderMobility, receiverMobility);
          double rxPowerDbm = m_loss->CalcRxPower (txPowerDbm, senderMobility, receiverMobility);
          NS_LOG_DEBUG ("propagation: txPower="<<txPowerDbm<<"dbm, rxPower="<<rxPowerDbm<<"dbm, "<<
                        "distance="<<senderMobility->GetDistanceFrom (receiverMobility)<<"m, delay="<<delay);
          Ptr<WifiPpdu> copy = Copy (ppdu);
          Ptr<Object> dstNetDevice = (*i)->GetDevice ();
          uint32_t dstNode;
          if (dstNetDevice == 0)
            {
              dstNode = 0xffffffff;
            }
          else
            {
              dstNode = dstNetDevice->GetObject<NetDevice> ()->GetNode ()->GetId ();
            }
          Simulator::ScheduleWithContext (dstNode,
                                          delay, &NslWifiChannel::Receive, this,
                                          (*i), copy, rxPowerDbm);
        }
    }
}
void
NslWifiChannel::Receive (Ptr<WifiPhy> phy, Ptr<WifiPpdu> ppdu, double rxPowerDbm)
{
  std::cout<<"NslWifichannel debug: Receive phytype = "<< phy->GetTypeId()<< std::endl;
    if ((rxPowerDbm + phy->GetRxGain ()) < phy->GetRxSensitivity ())
      {
        NS_LOG_INFO ("Received signal too weak to process: " << rxPowerDbm << " dBm");
        return;
      }
    phy->StartReceivePreamble (ppdu, DbmToW (rxPowerDbm + phy->GetRxGain ()));
}
*/

} // namespace ns3
