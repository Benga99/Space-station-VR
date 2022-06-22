using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SmokeController : MonoBehaviour
{
    public List<GameObject> smokes;
    public List<GameObject> smokes2;

    // Start is called before the first frame update
    void Start()
    {
        StartCoroutine(enableSmokeV2(smokes));
    }

    IEnumerator enableSmokeV1(List<GameObject> smok)
    {
        yield return new WaitForSeconds(3);

        foreach (var s in smok)
        {
            StartCoroutine(show(s));
            yield return new WaitForSeconds(0.3f);
        }
    }

    IEnumerator enableSmokeV2(List<GameObject> smok)
    {
        foreach (var s in smok)
        {
            s.SetActive(true);
            yield return new WaitForSeconds(0.2f);
        }
        yield return new WaitForSeconds(0);
        foreach (var s in smok)
        {
            //s.SetActive(false);
            s.GetComponent<ParticleSystem>().Stop();
            yield return new WaitForSeconds(0.1f);
        }

        yield return new WaitForSeconds(3f);
        StartCoroutine(enableSmokeV1(smokes2));
    }

    IEnumerator show(GameObject s)
    {
        s.SetActive(true);
        yield return new WaitForSeconds(1f);
        s.GetComponent<ParticleSystem>().Stop();
    }
}
