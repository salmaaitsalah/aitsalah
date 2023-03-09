#include "jammer-wifi-helper.h"
#include "ns3/jammer-wifi-phy.h"
#include "ns3/nsl-wifi-channel.h"
#include "ns3/simulator.h"
#include "ns3/propagation-loss-model.h"
#include "ns3/propagation-delay-model.h"
#include "ns3/error-rate-model.h"
#include "ns3/wifi-net-device.h"
#include "ns3/mobility-model.h"
#include "ns3/pointer.h"
#include "ns3/config.h"
#include "ns3/names.h"
#include "ns3/abort.h"
#include "ns3/log.h"

NS_LOG_COMPONENT_DEFINE ("JammerWifiHelper");
namespace ns3 {

NslWifiChannelHelper::NslWifiChannelHelper ()
{}


NslWifiChannelHelper
NslWifiChannelHelper::Default (void)
{
  NslWifiChannelHelper helper;
  helper.SetPropagationDelay ("ns3::ConstantSpeedPropagationDelayModel");
  helper.AddPropagationLoss ("ns3::LogDistancePropagationLossModel");
  return helper;
}

void
NslWifiChannelHelper::AddPropagationLoss (std::string type,
             std::string n0, const AttributeValue &v0,
             std::string n1, const AttributeValue &v1,
             std::string n2, const AttributeValue &v2,
             std::string n3, const AttributeValue &v3,
             std::string n4, const AttributeValue &v4,
             std::string n5, const AttributeValue &v5,
             std::string n6, const AttributeValue &v6,
             std::string n7, const AttributeValue &v7)
{
  ObjectFactory factory;
  factory.SetTypeId (type);
  factory.Set (n0, v0);
  factory.Set (n1, v1);
  factory.Set (n2, v2);
  factory.Set (n3, v3);
  factory.Set (n4, v4);
  factory.Set (n5, v5);
  factory.Set (n6, v6);
  factory.Set (n7, v7);
  m_propagationLoss.push_back (factory);
}

void
NslWifiChannelHelper::SetPropagationDelay (std::string type,
              std::string n0, const AttributeValue &v0,
              std::string n1, const AttributeValue &v1,
              std::string n2, const AttributeValue &v2,
              std::string n3, const AttributeValue &v3,
              std::string n4, const AttributeValue &v4,
              std::string n5, const AttributeValue &v5,
              std::string n6, const AttributeValue &v6,
              std::string n7, const AttributeValue &v7)
{
  ObjectFactory factory;
  factory.SetTypeId (type);
  factory.Set (n0, v0);
  factory.Set (n1, v1);
  factory.Set (n2, v2);
  factory.Set (n3, v3);
  factory.Set (n4, v4);
  factory.Set (n5, v5);
  factory.Set (n6, v6);
  factory.Set (n7, v7);
  m_propagationDelay = factory;
}

Ptr<NslWifiChannel>
NslWifiChannelHelper::Create (void) const
{
  Ptr<NslWifiChannel> channel = CreateObject<NslWifiChannel> ();
  Ptr<PropagationLossModel> prev = 0;
  for (std::vector<ObjectFactory>::const_iterator i = m_propagationLoss.begin (); i != m_propagationLoss.end (); ++i)
    {
      Ptr<PropagationLossModel> cur = (*i).Create<PropagationLossModel> ();
      if (prev != 0)
  {
    prev->SetNext (cur);
  }
      if (m_propagationLoss.begin () == i)
  {
    channel->SetPropagationLossModel (cur);
  }
      prev = cur;
    }
  Ptr<PropagationDelayModel> delay = m_propagationDelay.Create<PropagationDelayModel> ();
  channel->SetPropagationDelayModel (delay);
  return channel;
}
//----------------------------------------------------------------------------//

JammerWifiPhyHelper::JammerWifiPhyHelper ()
{
  m_phy.SetTypeId ("ns3::JammerWifiPhy");
  
}

JammerWifiPhyHelper
JammerWifiPhyHelper::Default (void)
{
  JammerWifiPhyHelper helper;
  helper.SetErrorRateModel ("ns3::NistErrorRateModel");
  return helper;
}

void
JammerWifiPhyHelper::SetChannel (Ptr<NslWifiChannel> channel)
{
  m_channel = channel;
}

void
JammerWifiPhyHelper::SetChannel (std::string channelName)
{
  Ptr<NslWifiChannel> channel = Names::Find<NslWifiChannel> (channelName);
  m_channel = channel;
}

Ptr<WifiPhy>
JammerWifiPhyHelper::Create (Ptr<Node> node, Ptr<NetDevice> device) const
{
  std::cout<<"JammerWifiPhyHelper debug: Create"<< std::endl;
  Ptr<JammerWifiPhy> phy = m_phy.Create<JammerWifiPhy> ();
  Ptr<ErrorRateModel> error = m_errorRateModel.Create<ErrorRateModel> ();
  phy->SetErrorRateModel (error);
  phy->SetChannel (m_channel);
 // phy->SetMobility (model);
  phy->SetDevice (device);
  phy->SetNode (node);
  phy->DoStart();
  std::cout<<"JammerWifiPhyHelper debug: Create phytype = "<< phy->GetTypeId()<< std::endl;
  return phy;
}

}