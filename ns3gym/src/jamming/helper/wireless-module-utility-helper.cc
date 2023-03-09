
#include "wireless-module-utility-helper.h"
#include "ns3/log.h"
#include "ns3/config.h"
#include "ns3/simulator.h"
#include "ns3/names.h"
#include "ns3/pointer.h"

NS_LOG_COMPONENT_DEFINE ("WirelessModuleUtilityHelper");

namespace ns3 {

WirelessModuleUtilityHelper::WirelessModuleUtilityHelper ()
{
  m_headerInclusionList.clear ();
  m_headerExclusionList.clear ();
  m_rssMeasurementCallback.Nullify ();
  m_wirelessUtility.SetTypeId ("ns3::WirelessModuleUtility");
}

WirelessModuleUtilityHelper::~WirelessModuleUtilityHelper ()
{
}

void
WirelessModuleUtilityHelper::SetWirelessModuleUtilityType (std::string type)
{
  NS_LOG_FUNCTION (this);
  m_wirelessUtility.SetTypeId (type);
}

std::string
WirelessModuleUtilityHelper::GetWirelessModuleUtilityType (void) const
{
  NS_LOG_FUNCTION (this);
  return m_wirelessUtility.GetTypeId ().GetName ();
}

void
WirelessModuleUtilityHelper::Set (std::string name, const AttributeValue &v)
{
  NS_LOG_FUNCTION (this);
  m_wirelessUtility.Set (name, v);
}

void
WirelessModuleUtilityHelper::SetInclusionList (std::vector<std::string> list)
{
  NS_LOG_FUNCTION (this);
  std::vector<std::string>::iterator i;
  for (i = list.begin (); i != list.end (); i++)
    {
      m_headerInclusionList.push_back (*i);
    }
}

void
WirelessModuleUtilityHelper::SetExclusionList (std::vector<std::string> list)
{
  NS_LOG_FUNCTION (this);
  std::vector<std::string>::iterator i;
  for (i = list.begin (); i != list.end (); i++)
    {
      m_headerExclusionList.push_back (*i);
    }
}

void
WirelessModuleUtilityHelper::SetRssMeasurementCallback (Callback<double> RssCallback)
{
  NS_LOG_FUNCTION (this);
  m_rssMeasurementCallback = RssCallback;
}

WirelessModuleUtilityContainer
WirelessModuleUtilityHelper::Install (Ptr<Node> node) const
{
  NS_LOG_FUNCTION (this << node);
  return Install (NodeContainer (node));
}

WirelessModuleUtilityContainer
WirelessModuleUtilityHelper::Install (NodeContainer c) const
{
  NS_LOG_FUNCTION (this);
  WirelessModuleUtilityContainer container;
  for (NodeContainer::Iterator i = c.Begin (); i != c.End (); ++i)
    {
      Ptr<WirelessModuleUtility> utility = DoInstall (*i);
      container.Add (utility);
    }
  return container;
}

WirelessModuleUtilityContainer
WirelessModuleUtilityHelper::Install (std::string nodeName) const
{
  Ptr<Node> node = Names::Find<Node> (nodeName);
  return Install (node);
}

WirelessModuleUtilityContainer
WirelessModuleUtilityHelper::InstallAll (void)
{
  return Install (NodeContainer::GetGlobal ());
}

/*
 * Private function starts here
 */

Ptr<WirelessModuleUtility>
WirelessModuleUtilityHelper::DoInstall (Ptr<Node> node) const
{
  NS_LOG_FUNCTION (this << node);

  Ptr<WirelessModuleUtility> util = node->GetObject<WirelessModuleUtility> ();
  if (util == NULL) // check if utility object already exist on node
    {
      util = m_wirelessUtility.Create<WirelessModuleUtility> ();
      if (util == NULL)
        {
          NS_FATAL_ERROR ("Can not create requested wireless utility object:" <<
                          m_wirelessUtility.GetTypeId ().GetName ());
          return NULL;
        }
      // setup

      util->SetRssMeasurementCallback (m_rssMeasurementCallback);
      // aggregate utility object to node
      node->AggregateObject (util);
    }
  else
    {
      NS_FATAL_ERROR ("WirelessModuleUtilityHelper:Utility already installed!");
      return NULL;
    }

  return util;
}

} // namespace ns3
