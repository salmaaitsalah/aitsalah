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

#include "mygym.h"
#include "ns3/datacollection-module-utility.h"
#include "ns3/object.h"
#include "ns3/core-module.h"
#include "ns3/wifi-module.h"
#include "ns3/node-list.h"
#include "ns3/log.h"
#include <sstream>
#include <iostream>

namespace ns3 {

NS_LOG_COMPONENT_DEFINE ("MyGymEnv");

NS_OBJECT_ENSURE_REGISTERED (MyGymEnv);

MyGymEnv::MyGymEnv ()
{
  NS_LOG_FUNCTION (this);
  nodeid = 0; //node id
  ls = 0; //number of successful rxok slots
  lc = 0; //number failed rx slots
  le = 0; //number of error rx slots (failed due to multi mpdu receiving fail)
  ltx = 0; // number tx slots
  minRxOkPowerW = 0; // minimum RX power for PHY layer in Watts currently is snr in replacement
  maxRxOkPowerW = 0; // maximum RX power for PHY layer in Watts
  currentChannel = 0; // current channel number
  contentionwindowid = 1; // cw sequencial number
  m_jammed = 0;
  m_numberofNeighbor = 0;

  parameterNum = 7;
}

MyGymEnv::~MyGymEnv ()
{
  NS_LOG_FUNCTION (this);
}

TypeId
MyGymEnv::GetTypeId (void)
{
  static TypeId tid = TypeId ("MyGymEnv")
                          .SetParent<OpenGymEnv> ()
                          .SetGroupName ("OpenGym")
                          .AddConstructor<MyGymEnv> ();
  return tid;
}

void
MyGymEnv::DoDispose ()
{
  NS_LOG_FUNCTION (this);
}

Ptr<OpenGymSpace>
MyGymEnv::GetActionSpace ()
{
  NS_LOG_FUNCTION (this);
  Ptr<OpenGymDiscreteSpace> space = CreateObject<OpenGymDiscreteSpace> (3);
  NS_LOG_UNCOND ("GetActionSpace: " << space);
  return space;
}

Ptr<OpenGymSpace>
MyGymEnv::GetObservationSpace ()
{
  float low = 0.0;
  float high = 1000000000.0;

  std::vector<uint32_t> shape = {
      parameterNum,
  };
  std::string dtype = TypeNameGet<uint32_t> ();
  Ptr<OpenGymBoxSpace> space = CreateObject<OpenGymBoxSpace> (low, high, shape, dtype);
  NS_LOG_UNCOND ("GetObservationSpace: " << space);
  return space;
}

bool
MyGymEnv::GetGameOver ()
{
  NS_LOG_FUNCTION (this);
  bool isGameOver = false;
  return isGameOver;
}

Ptr<OpenGymDataContainer>
MyGymEnv::GetObservation ()
{
  NS_LOG_FUNCTION (this);
  std::vector<uint32_t> shape = {
      parameterNum,
  };
  Ptr<OpenGymBoxContainer<uint32_t>> box = CreateObject<OpenGymBoxContainer<uint32_t>> (shape);
  box->AddValue (nodeid);
  box->AddValue (ls);
  box->AddValue (lc);
  box->AddValue (le);
  box->AddValue (ltx);
  // box->AddValue (minRxOkPowerW);
  // box->AddValue (maxRxOkPowerW);
  // box->AddValue (currentChannel);
  // box->AddValue (contentionwindowid);
  box->AddValue (m_numberofNeighbor);
  box->AddValue (m_jammed);

  // NS_LOG_UNCOND ("MyGetObservation: " << box);
  return box;
}

float
MyGymEnv::GetReward ()
{
  NS_LOG_FUNCTION (this);
  float reward = 1.0;
  return reward;
}

std::string
MyGymEnv::GetExtraInfo ()
{
  NS_LOG_FUNCTION (this);
  std::string myInfo = "info";
  // NS_LOG_UNCOND ("MyGetExtraInfo: " << myInfo);
  return myInfo;
}

bool
MyGymEnv::ExecuteActions (Ptr<OpenGymDataContainer> action)
{
  NS_LOG_FUNCTION (this);
  return true;
}

void
MyGymEnv::TestTrace (int32_t oldValue, int32_t newValue)
{
  // NS_LOG_UNCOND ("Traced test value from " << oldValue << " to " << newValue << std::endl);
  return;
}

void
MyGymEnv::DatumTrace (Ptr<MyGymEnv> env, ns3::DataCollectionModuleUtility::datum oldValue,
                      ns3::DataCollectionModuleUtility::datum newValue)
{
  // NS_LOG_UNCOND ("Traced nodeid " << newValue.nodeid << std::endl);
  // NS_LOG_UNCOND ("Traced cwid from " << oldValue.contentionwindowid << " to "
  //  << newValue.contentionwindowid << std::endl);
  // NS_LOG_UNCOND ("Traced channel  from " << oldValue.currentChannel << " to "
  //                                        << newValue.currentChannel << std::endl);
  env->nodeid = newValue.nodeid;
  env->ls = newValue.ls;
  env->lc = newValue.lc;
  env->le = newValue.le;
  env->ltx = newValue.ltx;
  // env->minRxOkPowerW = newValue.minRxOkPowerW;
  // env->maxRxOkPowerW = newValue.maxRxOkPowerW;
  env->currentChannel = newValue.currentChannel;
  // env->contentionwindowid = newValue.contentionwindowid;
  env->m_numberofNeighbor = newValue.m_numberofNeighbor;
  env->m_jammed = newValue.m_jammed;
  if (env->currentChannel == 178)
    env->Notify ();
  return;
}
} // namespace ns3
