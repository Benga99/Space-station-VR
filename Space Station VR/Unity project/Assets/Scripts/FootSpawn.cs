using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class FootSpawn : MonoBehaviour
{
    [SerializeField]
    private GameObject foot;

    [SerializeField]
    List<Vector3> positionsRight;

    [SerializeField]
    List<Vector3> positionsLeft;

    [SerializeField]
    private Image radialImage;

    [SerializeField]
    private float seconds;
    [SerializeField]
    private TextMeshProUGUI secondsText;

    void Start()
    {
        StartCoroutine(Spawn());
        StartCoroutine(runClock());
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private IEnumerator Spawn()
    {
        for(int i = 0; i < positionsRight.Count; i++)
        {
            GameObject right = Instantiate(foot, positionsRight[i], Quaternion.Euler(0, -24, 0));
            StartCoroutine(reactivateAlpha(right));
            yield return new WaitForSeconds(1);

            GameObject left = Instantiate(foot, positionsLeft[i], Quaternion.Euler(180, 24, 0));
            StartCoroutine(reactivateAlpha(left));
            yield return new WaitForSeconds(1);

            
        }
    }

    private IEnumerator reactivateAlpha(GameObject obj)
    {
        float i = 0;
        while(obj.GetComponent<MeshRenderer>().material.color.a < 1)
        {
            obj.GetComponent<MeshRenderer>().material.color = new Color(obj.GetComponent<MeshRenderer>().material.color.r,
                                                                    obj.GetComponent<MeshRenderer>().material.color.g,
                                                                    obj.GetComponent<MeshRenderer>().material.color.b,
                                                                    i);
            i += 0.001f;
            yield return new WaitForEndOfFrame();
        }
        
    }

    private IEnumerator runClock()
    {
        bool colorChanged = false;
        float secondsPassed = 0f;
        while(radialImage.GetComponent<Image>().fillAmount > 0)
        {
            if(radialImage.GetComponent<Image>().fillAmount < 0.26f && !colorChanged)
            {
                colorChanged = true;
                radialImage.GetComponent<Image>().color = Color.red;

            }
            secondsPassed += Time.fixedDeltaTime;

            secondsText.text = $"{(int)((seconds - secondsPassed) / 60)}:{(int)((seconds - secondsPassed) % 60):D2}";

            radialImage.GetComponent<Image>().fillAmount = Mathf.InverseLerp(0, seconds, seconds - secondsPassed);
            yield return new WaitForFixedUpdate();
        }
        radialImage.transform.parent.gameObject.SetActive(false);
    }


}
