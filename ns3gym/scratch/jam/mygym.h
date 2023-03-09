/* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2018 Technische Universität Berlin
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
 * Author: Piotr Gawlowicz <gawlowicz@tkn.tu-berlin.de>
 */

#ifndef MY_GYM_ENTITY_H
#define MY_GYM_ENTITY_H

#include "ns3/stats-module.h"
#include "ns3/opengym-module.h"
#include "ns3/spectrum-module.h"
#include "ns3/datacollection-module-utility.h"

namespace ns3 {

class Node;
class WifiMacQueue;
class Packet;

class MyGymEnv : public OpenGymEnv
{
public:
  MyGymEnv ();
  virtual ~MyGymEnv ();
  static TypeId GetTypeId (void);
  virtual void DoDispose ();

  Ptr<OpenGymSpace> GetObservationSpace ();
  Ptr<OpenGymSpace> GetActionSpace ();
  Ptr<OpenGymDataContainer> GetObservation ();
  float GetReward ();
  bool GetGameOver ();
  std::string GetExtraInfo ();
  bool ExecuteActions (Ptr<OpenGymDataContainer> action);

  static void TestTrace (int32_t oldValue, int32_t newValue);
  static void DatumTrace (Ptr<MyGymEnv> env, ns3::DataCollectionModuleUtility::datum oldValue,
                          ns3::DataCollectionModuleUtility::datum newValue);

private:
  uint32_t nodeid; //node id
  uint32_t ls; //number of successful rxok slots
  uint32_t lc; //number failed rx slots
  uint32_t le; //number of error rx slots (failed due to multi mpdu receiving fail)
  uint32_t ltx; // number tx slots
  double minRxOkPowerW; // minimum RX power for PHY layer in Watts currently is snr in replacement
  double maxRxOkPowerW; // maximum RX power for PHY layer in Watts
  uint16_t currentChannel; // current channel number
  uint32_t contentionwindowid; // cw sequencial number
  bool m_jammed;
  uint32_t m_numberofNeighbor;

  uint32_t parameterNum;
};

} // namespace ns3

#endif // MY_GYM_ENTITY_H
