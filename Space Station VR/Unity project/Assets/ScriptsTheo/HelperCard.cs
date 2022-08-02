using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HelperCard : MonoBehaviour
{
    [SerializeField]
    private GameObject HelpCard1;
    [SerializeField]
    private GameObject HelpCard2;
    [SerializeField]
    private GameObject HelpCard3;
    [SerializeField]
    private GameObject HelpCard4;
    [SerializeField]
    private GameObject HelpCard5;
    [SerializeField]
    private GameObject HelpCard6;

    public bool showCard1 = false;
    public bool showCard2 = false;
    public bool showCard3 = false;
    public bool showCard4 = false;
    public bool showCard5 = false;
    public bool showCard6 = false;

    private bool card1revealed = false;
    private bool card2revealed = false;
    private bool card3revealed = false;
    private bool card4revealed = false;
    private bool card5revealed = false;
    private bool card6revealed = false;

    private Vector3 finalPosition = new Vector3(0f, 0f, 0.32f);
    private Vector3 finalRotation = new Vector3(0, 90, 0);

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (showCard1 && !card1revealed)
        {
            card1revealed = true;
            StartCoroutine(showCard(HelpCard1));
        }
        if (showCard2 && !card2revealed)
        {
            card2revealed = true;
            StartCoroutine(showCard(HelpCard2));
        }
        if (showCard3 && !card3revealed)
        {
            card3revealed = true;
            StartCoroutine(showCard(HelpCard3));
        }
        if (showCard4 && !card4revealed)
        {
            card4revealed = true;
            StartCoroutine(showCard(HelpCard4));
        }
        if (showCard5 && !card5revealed)
        {
            card5revealed = true;
            StartCoroutine(showCard(HelpCard5));
        }
        if (showCard6 && !card6revealed)
        {
            card6revealed = true;
            StartCoroutine(showCard(HelpCard6));
        }
    }


    IEnumerator showCard(GameObject card)
    {
        card.SetActive(true);
        card.transform.localScale = new Vector3(0.3333f, 0.01f, 0.3333f);
        card.transform.LeanMoveLocal(finalPosition, 2f).setEaseInOutCubic();
        yield return new WaitForSeconds(1.5f);


        while(card.transform.localEulerAngles.y % 181 < 180)
        {
            card.transform.Rotate(0, 3, 0);
            yield return new WaitForEndOfFrame();
        }
        card.transform.LeanScaleY(0.3333f, 1f).setEaseInOutBounce();
        yield return new WaitForSeconds(2f);
        Debug.Log("Canceled");
        LeanTween.cancel(this.gameObject);
    }
}
