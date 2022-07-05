using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class DartsGame : MonoBehaviour
{
    private List<GameObject> dartPoints = new List<GameObject>();
    public Text dartNumbers;
    public int darts = 0;

    private void OnTriggerEnter(Collider other)
    {
        if (other.gameObject.tag == "Dart" && !dartPoints.Contains(other.gameObject))
        {
            if (dartNumbers.gameObject.activeInHierarchy == false)
            {
                dartNumbers.gameObject.SetActive(true);
            }
            other.gameObject.GetComponent<Rigidbody>().constraints = RigidbodyConstraints.FreezeAll;
            darts++;
            dartNumbers.text = darts.ToString() + " / 3";
            dartPoints.Add(other.gameObject);
        }
    }
}
